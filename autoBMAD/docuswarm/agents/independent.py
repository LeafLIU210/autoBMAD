"""Independent Agent Implementation - Story 2.6, Updated for Story 7.3, 7.4, and 8.4.

This module provides the IndependentAgent class which:
- Loads BMAD persona from nodes/{node_id}/persona.json
- Calls LLM with Kimi K2.5 Agent mode (temperature 0.7, max_tokens 32768)
- Tool calling handled entirely by SDK auto-dispatch (Story 8.4)
- Generates questions with priorities: blocking, clarifying, optional
- Preserves private reasoning (NOT shared with Evaluator)
- Returns structured output matching IndependentOutput schema
- Updated to support KimiSessionManager (Story 7.3)
- Updated to use Session API with Wire messages (Story 7.4)
- Removed manual tool parsing - SDK handles all tool dispatch (Story 8.4)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, override

import structlog

# Import SDK types for Session API (Story 7.4)
from kimi_agent_sdk import Message
from kimi_agent_sdk._aggregator import MessageAggregator

from autoBMAD.docuswarm.agents.base import BaseAgent
from autoBMAD.docuswarm.agents.persona import PersonaLoader
from autoBMAD.docuswarm.config import Config as AgentConfig
from autoBMAD.docuswarm.exceptions import LLMError
from autoBMAD.docuswarm.llm.response import (
    ResponseParseError,
    ValidationError,
    extract_json,
    validate_independent_output,
)
from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager

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
        config: AgentConfig,
        session_manager: KimiSessionManager,
        node_id: str = "dev",
        project_root: Path | None = None,
    ) -> None:
        """Initialize the IndependentAgent.

        Args:
            config: Agent configuration object.
            session_manager: KimiSessionManager for SDK interactions.
            node_id: The node identifier for loading persona from nodes/{node_id}/persona.json.
            project_root: Root directory of the project. If None, uses cwd.

        Raises:
            PersonaLoadError: If persona loading fails.
        """
        super().__init__(config, session_manager=session_manager)
        self.node_id = node_id
        self.project_root = project_root or Path.cwd()

        # Story 11.1: Instance variables for agent_file and work_dir
        self._agent_file: Path | None = None
        self._work_dir: Path | None = None

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
        instructions = """## Agent Instructions

You are an Independent Agent that creates deliverables and generates questions.

## Execution Workflow

1. **Create Deliverable**: Use the 'create_deliverable' tool to save your document
   - The tool accepts: title (string) and content (Markdown string)
   - This writes the deliverable to a .md file

2. **Generate Questions**: Formulate follow-up questions with priorities

3. **Return Execution Report**: After using tools, you MUST return a JSON response

## CRITICAL: Output Format

After executing tools, you MUST respond with ONLY this exact JSON structure:

```json
{
  "deliverable": {
    "title": "Brief title of what you created",
    "content": "Brief summary (1-2 sentences, NOT the full document)"
  },
  "questions": [
    {
      "question": "Question text?",
      "priority": "blocking | clarifying | optional",
      "context": "Context or rationale for this question"
    }
  ],
  "action": "create_deliverable"
}
```

**IMPORTANT**:
- The entire response must be valid JSON parseable by json.loads()
- Do NOT include markdown formatting outside the JSON
- The "deliverable.content" field is just a SUMMARY, not the full document
- The full document was already saved via the tool

## Question Priorities

- **blocking**: Must be answered before proceeding
- **clarifying**: Help refine the deliverable
- **optional**: Nice-to-have for future consideration

## Example

Correct response after creating a document:
```json
{
  "deliverable": {
    "title": "Project Analysis Report",
    "content": "Created comprehensive analysis covering architecture and requirements."
  },
  "questions": [
    {
      "question": "Should we include performance benchmarks?",
      "priority": "clarifying",
      "context": "To provide quantitative performance data for stakeholders"
    }
  ],
  "action": "create_deliverable"
}
```

Incorrect response (will cause parsing error):
```
## Summary

I have created a Project Analysis Report...
```
"""
        return f"{persona_prompt}\n\n{instructions}"

    async def _call_llm(self, user_message: str) -> list[Message]:
        """Call the LLM using Session API (Story 7.4, 8.4).

        Uses session_manager.create_session() with mode="agent" and yolo=True
        for automatic tool call approval. Processes Wire messages via
        MessageAggregator to collect complete responses.

        Args:
            user_message: The user message to send.

        Returns:
            list[Message] from the LLM.

        Raises:
            LLMCallError: If the LLM call fails.
            SessionError: If session creation fails.
        """
        return await self._call_llm_via_session(user_message)

    async def _call_llm_via_session(self, user_message: str) -> list[Message]:
        """Call LLM via Session API with Wire message processing (Story 7.4).

        Creates a session with mode="agent" and yolo=True for auto-approval.
        Uses MessageAggregator to collect streaming Wire messages into
        complete Message objects.

        Args:
            user_message: The user message to send.

        Returns:
            list[Message] from the LLM.

        Raises:
            SessionError: If session creation or message processing fails.
            LLMCallError: On SDK exceptions like MaxStepsReached, RunCancelled.
        """
        from kimi_agent_sdk import MaxStepsReached, RunCancelled
        from kimi_agent_sdk._aggregator import MessageAggregator
        from kimi_cli.wire.types import ApprovalRequest

        system_prompt = self._format_system_prompt()

        # Build full prompt with system instructions
        full_prompt = f"{system_prompt}\n\nUser request: {user_message}"

        session = None
        messages: list[Any] = []
        try:
            # Create session with mode="agent" and yolo=True for auto-approval (Story 7.4)
            # Story 11.1: Also pass agent_file for tool registration
            # session_manager is guaranteed non-None by caller (_call_llm checks)
            sm = self.session_manager
            assert sm is not None

            # Story 11.1: Pass agent_file to create_session (work_dir is set on session_manager)
            session = await sm.create_session(
                mode="agent",
                yolo=True,
                agent_file=self._agent_file,
            )

            # Process wire messages with aggregator
            aggregator: MessageAggregator = MessageAggregator()

            async for wire_msg in session.prompt(full_prompt):
                # Handle ApprovalRequest - auto-approve for independent agent (Story 7.4)
                if isinstance(wire_msg, ApprovalRequest):
                    # yolo=True should auto-approve, but handle explicitly just in case
                    wire_msg.resolve("approve")
                    self.logger.debug("approval_auto_resolved", request_id=wire_msg.id)
                    continue

                # Feed wire messages to aggregator and collect completed messages
                for msg in aggregator.feed(wire_msg):
                    messages.append(msg)

            # Flush final messages
            for msg in aggregator.flush():
                messages.append(msg)

            # Return messages
            if not messages:
                raise LLMCallError("No messages returned from session")

            return messages

        except MaxStepsReached as e:
            # Handle MaxStepsReached gracefully - return partial messages (Story 7.4)
            self.logger.warning("max_steps_reached", error=str(e))
            # Return partial messages if available
            if messages:
                return messages
            raise LLMCallError(f"Max steps reached: {e}") from e

        except RunCancelled as e:
            # Handle RunCancelled gracefully - return gracefully (Story 7.4)
            self.logger.info("run_cancelled", error=str(e))
            # Return partial messages if available
            if messages:
                return messages
            raise LLMCallError(f"Run cancelled: {e}") from e

        except LLMError:
            # Re-raise DocuSwarm LLM errors as-is
            raise

        except Exception as e:
            self.logger.error("session_call_failed", error=str(e))
            raise SessionError(f"Session call failed: {e}") from e

        finally:
            # Clean up session
            if session is not None:
                await session.close()

    def _extract_content_from_messages(self, messages: list[Message]) -> str:
        """Extract text content from aggregated messages.

        Args:
            messages: List of Message objects from aggregator.

        Returns:
            Extracted text content, or empty string if none found.
        """
        # Get content from the last message with content
        for msg in reversed(messages):
            if hasattr(msg, "content") and msg.content:
                # Use SDK's extract_text() method for proper TextPart extraction
                # This handles both string content and list of content parts
                if hasattr(msg, "extract_text"):
                    return msg.extract_text()  # type: ignore[return-value]
                return str(msg.content)  # type: ignore[return-value]
        return ""

    def _parse_response(self, response: list[Message]) -> IndependentOutput:
        """Parse and validate LLM response against IndependentOutput schema.

        Args:
            response: The list[Message] from the LLM.

        Returns:
            Parsed and validated output dictionary.

        Raises:
            ResponseParseAgentError: If parsing or validation fails.
        """
        content = self._extract_content_from_messages(response)

        if not content or not content.strip():
            raise ResponseParseAgentError("Empty response from LLM")

        # Try to extract JSON from the response
        data: dict[str, Any]  # Type annotation for type checker
        try:
            data = extract_json(content)
        except ResponseParseError as e:
            # Fallback: If LLM returned pure Markdown, construct JSON
            if content.strip().startswith(("#", "##", "###")) or "Summary" in content[:100]:
                self.logger.warning(
                    "llm_returned_markdown_fallback",
                    attempting_fallback=True,
                    content_preview=content[:200],
                )

                # Extract title from first heading
                import re as re_module

                title_match = re_module.search(r"^#+\s*(.+)$", content, re_module.MULTILINE)
                title = title_match.group(1) if title_match else "LLM Generated Document"

                # Use full content as summary (will be trimmed in validation if needed)
                data = {
                    "deliverable": {
                        "title": title,
                        "content": content[:500] + "..." if len(content) > 500 else content,
                    },
                    "questions": [],
                    "action": "create_deliverable",
                }

                self.logger.info(
                    "markdown_fallback_success",
                    constructed_title=title,
                    content_length=len(content),
                )
            else:
                self.logger.error("response_parse_failed", error=str(e), content=content[:200])
                raise ResponseParseAgentError(f"Failed to parse response: {e}") from e

        # Validate against IndependentOutput schema
        try:
            validate_independent_output(data)
        except ValidationError as e:
            self.logger.error("response_validation_failed", error=str(e), data=data)
            raise ResponseParseAgentError(f"Response validation failed: {e}") from e

        return data

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
        # agent_file is relative to project root: docuswarm/agents/configs/independent_agent.yaml
        # project_root should be the autoBMAD directory (parent of docuswarm)
        self._agent_file = (
            self.project_root / "docuswarm" / "agents" / "configs" / "independent_agent.yaml"
        )
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
        # The work_dir must be set on KimiSessionManager constructor, not create_session()
        from kaos.path import KaosPath

        from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager

        # Create new session manager with work_dir for this pipeline execution
        pipeline_session_manager = KimiSessionManager(
            work_dir=KaosPath(str(output_dir)),
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


# Convenience function for creating IndependentAgent
def create_independent_agent(
    config: AgentConfig,
    session_manager: KimiSessionManager,
    node_id: str = "dev",
    project_root: Path | None = None,
) -> IndependentAgent:
    """Create an IndependentAgent with configured session manager.

    Args:
        config: Agent configuration.
        session_manager: KimiSessionManager for SDK interactions.
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

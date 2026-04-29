"""
DocuSwarm Approval Handler Module

Provides a configurable approval handler for SDK tool calls that:
- Auto-approves safe operations (create_deliverable, update_context, read_file)
- Rejects dangerous operations (write_file, execute_command, delete_file)
- Approves unknown actions with conservative policy (approve single)
- Supports auto_approve_all flag for yolo mode

Example:
    >>> from autoBMAD.docuswarm.llm.approval import DocuSwarmApprovalHandler
    >>>
    >>> handler = DocuSwarmApprovalHandler()
    >>> # Use handler.handle as the approval_handler_fn callback
    >>> session = await Session.create(
    ...     work_dir=work_dir,
    ...     approval_handler_fn=handler.handle
    ... )
"""

from __future__ import annotations

from typing import Any

import structlog

# Default safe actions that are auto-approved
DEFAULT_AUTO_APPROVE_ACTIONS: set[str] = {
    "create_deliverable",
    "update_context",
    "read_file",
}

# Default dangerous actions that are rejected
DEFAULT_REJECT_ACTIONS: set[str] = {
    "write_file",
    "execute_command",
    "delete_file",
}

# Structured logger for this module
logger: structlog.BoundLogger = structlog.get_logger(__name__)


class DocuSwarmApprovalHandler:
    """
    Configurable approval handler for SDK tool calls.

    This handler implements a security-focused approval policy:
    - Auto-approves known safe operations
    - Rejects known dangerous operations
    - Conservatively approves unknown operations (single approval)

    Attributes:
        auto_approve_actions: Set of action names that are auto-approved.
        reject_actions: Set of action names that are rejected.
        auto_approve_all: If True, bypasses all checks (yolo mode).
        unknown_action_policy: Policy for unknown actions ("approve" or "reject").

    Example:
        >>> handler = DocuSwarmApprovalHandler()
        >>> # Register with session
        >>> session = await Session.create(
        ...     work_dir=work_dir,
        ...     approval_handler_fn=handler.handle
        ... )
    """

    def __init__(
        self,
        auto_approve_actions: set[str] | None = None,
        reject_actions: set[str] | None = None,
        auto_approve_all: bool = False,
        unknown_action_policy: str = "reject",  # M1 Fix: default to reject for least privilege
    ) -> None:
        """
        Initialize the DocuSwarmApprovalHandler.

        Args:
            auto_approve_actions: Set of action names to auto-approve.
                Defaults to {"create_deliverable", "update_context", "read_file"}.
            reject_actions: Set of action names to reject.
                Defaults to {"write_file", "execute_command", "delete_file"}.
            auto_approve_all: If True, approve all actions without checking.
                Use this for yolo mode. Defaults to False.
            unknown_action_policy: Policy for unknown actions.
                Must be "approve" or "reject". Defaults to "reject" (M1 Fix).
        """
        self._auto_approve_actions = auto_approve_actions or DEFAULT_AUTO_APPROVE_ACTIONS.copy()
        self._reject_actions = reject_actions or DEFAULT_REJECT_ACTIONS.copy()
        self._auto_approve_all = auto_approve_all
        self._unknown_action_policy = unknown_action_policy

        logger.debug(
            "approval_handler_initialized",
            auto_approve_actions=list(self._auto_approve_actions),
            reject_actions=list(self._reject_actions),
            auto_approve_all=auto_approve_all,
            unknown_action_policy=unknown_action_policy,
        )

    @property
    def auto_approve_actions(self) -> set[str]:
        """Get the set of auto-approved action names."""
        return self._auto_approve_actions

    @property
    def reject_actions(self) -> set[str]:
        """Get the set of rejected action names."""
        return self._reject_actions

    @property
    def auto_approve_all(self) -> bool:
        """Get whether yolo mode is enabled."""
        return self._auto_approve_all

    def handle(self, request: Any) -> None:
        """
        Handle an approval request from the SDK.

        This method is the callback function for the SDK's approval_handler_fn
        parameter. It implements the approval policy based on the action name.

        Args:
            request: The ApprovalRequest from the SDK containing:
                - id: Unique request identifier
                - tool_call_id: ID of the tool call
                - sender: Name of the sender
                - action: The action to approve/reject
                - description: Human-readable description

        Note:
            This method uses synchronous resolution. The SDK will handle
            async/sync conversion automatically.
        """
        action = request.action

        # Yolo mode: approve everything
        if self._auto_approve_all:
            logger.info(
                "approval_decision",
                action=action,
                decision="approve",
                reason="auto_approve_all=true (yolo mode)",
            )
            request.resolve("approve")
            return

        # Check auto-approve list
        if action in self._auto_approve_actions:
            logger.info(
                "approval_decision",
                action=action,
                decision="approve",
                reason="auto_approve_actions",
            )
            request.resolve("approve")
            return

        # Check reject list
        if action in self._reject_actions:
            logger.info(
                "approval_decision",
                action=action,
                decision="reject",
                reason="reject_actions",
            )
            request.resolve("reject")
            return

        # Unknown action: apply conservative policy (approve single)
        logger.info(
            "approval_decision",
            action=action,
            decision=self._unknown_action_policy,
            reason="unknown_action_policy",
        )
        request.resolve(self._unknown_action_policy)


# Define public API
__all__ = [
    "DocuSwarmApprovalHandler",
    "DEFAULT_AUTO_APPROVE_ACTIONS",
    "DEFAULT_REJECT_ACTIONS",
]

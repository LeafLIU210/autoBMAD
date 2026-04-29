"""P1: Approval handler tests (M1).

Ensures unknown actions are rejected by default.
"""

from __future__ import annotations

import pytest

from autoBMAD.docuswarm.llm.approval import DocuSwarmApprovalHandler


class TestApprovalHandlerDefaultPolicy:
    """T1.1: Default unknown_action_policy must be 'reject'."""

    def test_default_unknown_action_is_rejected(self) -> None:
        handler = DocuSwarmApprovalHandler()
        assert handler._unknown_action_policy == "reject"

    def test_explicit_approve_policy_allowed(self) -> None:
        handler = DocuSwarmApprovalHandler(unknown_action_policy="approve")
        assert handler._unknown_action_policy == "approve"

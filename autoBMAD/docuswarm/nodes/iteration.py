"""Iteration Control Implementation - Story 5.2.

This module provides iteration control for nodes within the pipeline:
- IterationHistory: Stores individual iteration data
- NodeIterationState: Manages state for a single node's iterations
- IterationController: Controls iteration flow across multiple nodes

The controller tracks iteration counts per node, enforces maximum iterations,
preserves iteration history for audit/debugging, and aggregates feedback
for subsequent iterations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from structlog import BoundLogger as StructlogBoundLogger


# Verdicts that should stop iteration
TERMINAL_VERDICTS = {"APPROVED", "FORCE_APPROVED", "BLOCKED"}


@dataclass
class IterationHistory:
    """Stores data for a single iteration.

    Attributes:
        iteration: The iteration number (1-indexed).
        verdict: The verdict from the evaluator (APPROVED, NEEDS_REVISION, etc.).
        alignment_score: The alignment score from the evaluator.
        feedback: The feedback text for this iteration.
        issues: List of issues identified in this iteration.
        suggestions: List of suggestions for improvement.
        timestamp: When this iteration was recorded.
    """

    iteration: int = 0
    verdict: str | None = None
    alignment_score: float = 0.0
    feedback: str = ""
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class NodeIterationState:
    """Manages iteration state for a single node.

    Attributes:
        node_id: The unique identifier for this node.
        current_iteration: The current iteration number (1-indexed).
        history: List of all iteration history entries.
    """

    node_id: str = ""
    current_iteration: int = 0
    history: list[IterationHistory] = field(default_factory=list)


class IterationController:
    """Controls iteration flow within nodes.

    This controller:
    - Tracks iteration count per node throughout pipeline execution
    - Enforces maximum number of iterations (default: 3, configurable)
    - Passes feedback from each iteration to the next
    - Preserves iteration history for audit and debugging
    - Logs all key events via structlog

    The controller does NOT make iteration decisions - it only tracks state
    and provides data; the caller (e.g., DualAgentNode) determines the loop.

    Thread-safety: Uses a regular dict for state. For parallel node execution,
    consider adding threading.Lock for state dict access.

    Example:
        controller = IterationController(max_iterations=3)

        # Start first iteration
        controller.start_iteration("my_node")

        # Record results
        controller.record_iteration(
            node_id="my_node",
            verdict="NEEDS_REVISION",
            alignment_score=0.65,
            issues=["Issue 1", "Issue 2"],
            suggestions=["Fix issue 1", "Fix issue 2"],
        )

        # Check if should iterate
        if controller.should_iterate("my_node"):
            # Get accumulated feedback for next iteration
            feedback = controller.get_accumulated_feedback("my_node")
            # ... pass feedback to next iteration ...

        # Repeat until approved or max iterations reached
    """

    DEFAULT_MAX_ITERATIONS = 3

    def __init__(self, max_iterations: int = DEFAULT_MAX_ITERATIONS) -> None:
        """Initialize the IterationController.

        Args:
            max_iterations: Maximum number of iterations per node (default: 3).
        """
        self.max_iterations = max_iterations
        self._node_states: dict[str, NodeIterationState] = {}
        self.logger: StructlogBoundLogger = structlog.get_logger().bind(
            component=self.__class__.__name__
        )

    def start_iteration(self, node_id: str) -> int:
        """Start a new iteration for the specified node.

        Initializes state for new nodes or increments iteration counter for existing nodes.

        Args:
            node_id: The unique identifier for the node.

        Returns:
            The current iteration number (1-indexed).
        """
        if node_id not in self._node_states:
            # Initialize new node state
            self._node_states[node_id] = NodeIterationState(
                node_id=node_id,
                current_iteration=1,
            )
            self.logger.info(
                "iteration_start",
                node_id=node_id,
                iteration=1,
            )
            return 1
        else:
            # Increment existing iteration
            state = self._node_states[node_id]
            state.current_iteration += 1
            iteration = state.current_iteration

            self.logger.info(
                "iteration_start",
                node_id=node_id,
                iteration=iteration,
            )
            return iteration

    def record_iteration(
        self,
        node_id: str,
        verdict: str,
        alignment_score: float,
        issues: list[str] | None = None,
        suggestions: list[str] | None = None,
        feedback: str = "",
    ) -> None:
        """Record iteration results in history.

        Args:
            node_id: The unique identifier for the node.
            verdict: The verdict from the evaluator.
            alignment_score: The alignment score from the evaluator.
            issues: List of issues identified (optional).
            suggestions: List of suggestions for improvement (optional).
            feedback: Additional feedback text (optional).
        """
        # Ensure state exists
        if node_id not in self._node_states:
            self._node_states[node_id] = NodeIterationState(node_id=node_id)

        state = self._node_states[node_id]
        iteration = state.current_iteration

        history_entry = IterationHistory(
            iteration=iteration,
            verdict=verdict,
            alignment_score=alignment_score,
            feedback=feedback,
            issues=issues or [],
            suggestions=suggestions or [],
            timestamp=datetime.now(),
        )

        state.history.append(history_entry)

        self.logger.info(
            "iteration_recorded",
            node_id=node_id,
            iteration=iteration,
            verdict=verdict,
            alignment_score=alignment_score,
        )

    def should_iterate(self, node_id: str) -> bool:
        """Determine if another iteration should occur.

        Returns False if:
        - Verdict is APPROVED, FORCE_APPROVED, or BLOCKED (terminal verdicts)
        - Maximum iterations reached

        Returns True if:
        - Verdict is NEEDS_REVISION and under max iterations

        Args:
            node_id: The unique identifier for the node.

        Returns:
            True if another iteration should occur, False otherwise.
        """
        if node_id not in self._node_states:
            return False

        state = self._node_states[node_id]
        if not state.history:
            return False

        # Get the latest verdict
        latest = state.history[-1]

        # Check for terminal verdicts
        if latest.verdict in TERMINAL_VERDICTS:
            self.logger.info(
                "iteration_stopped_terminal",
                node_id=node_id,
                verdict=latest.verdict,
            )
            return False

        # Check max iterations
        if state.current_iteration >= self.max_iterations:
            self.logger.warning(
                "max_iterations_reached",
                node_id=node_id,
                current_iteration=state.current_iteration,
                max_iterations=self.max_iterations,
            )
            return False

        return True

    def get_accumulated_feedback(self, node_id: str) -> str:
        """Aggregate feedback from all iterations up to and including the last non-terminal verdict.

        Stops accumulating when a terminal verdict (APPROVED, FORCE_APPROVED, BLOCKED)
        is encountered.

        Args:
            node_id: The unique identifier for the node.

        Returns:
            Formatted feedback string for all iterations, or empty string if no history.
        """
        if node_id not in self._node_states:
            return ""

        state = self._node_states[node_id]
        if not state.history:
            return ""

        feedback_parts: list[str] = []

        for history_entry in state.history:
            # Stop at terminal verdict (don't include feedback after approval)
            if history_entry.verdict in TERMINAL_VERDICTS:
                break

            feedback = self._generate_feedback(history_entry)
            if feedback:
                feedback_parts.append(feedback)

        return "\n\n".join(feedback_parts)

    def _generate_feedback(self, history: IterationHistory) -> str:
        """Generate formatted feedback from a single iteration history entry.

        Args:
            history: The iteration history entry.

        Returns:
            Formatted feedback string, or empty string for terminal verdicts.
        """
        # Don't generate feedback for terminal verdicts
        if history.verdict in TERMINAL_VERDICTS:
            return ""

        lines: list[str] = [
            f"## Iteration {history.iteration}",
            f"**Alignment Score**: {history.alignment_score:.2f}",
            f"**Verdict**: {history.verdict}",
            "",
        ]

        if history.issues:
            lines.append("### Issues")
            for issue in history.issues:
                lines.append(f"- {issue}")
            lines.append("")

        if history.suggestions:
            lines.append("### Suggestions")
            for suggestion in history.suggestions:
                lines.append(f"- {suggestion}")
            lines.append("")

        if history.feedback:
            lines.append("### Feedback")
            lines.append(history.feedback)
            lines.append("")

        return "\n".join(lines).strip()

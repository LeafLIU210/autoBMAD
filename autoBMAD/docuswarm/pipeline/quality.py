"""Quality evaluation module - Story 5.1.

This module provides quality threshold configuration and verdict determination
for the DocuSwarm pipeline. It enables consistent quality decisions across
all nodes with configurable thresholds and node-specific overrides.

Key components:
- QualityThresholds: Dataclass for approval and escalation thresholds
- QualityConfig: Configuration class with defaults and node-specific overrides
- VerdictDeterminer: Determines verdict based on alignment score and thresholds
"""

from dataclasses import dataclass
from enum import Enum


class Verdict(Enum):
    """Possible verdict outcomes for quality evaluation.

    - APPROVED: Score meets or exceeds approval threshold
    - NEEDS_REVISION: Score below approval threshold, iterations remaining
    - FORCE_APPROVED: At max iterations, score meets escalation threshold
    - BLOCKED: At max iterations, score below escalation threshold
    """

    APPROVED = "APPROVED"
    NEEDS_REVISION = "NEEDS_REVISION"
    FORCE_APPROVED = "FORCE_APPROVED"
    BLOCKED = "BLOCKED"


@dataclass
class QualityThresholds:
    """Quality thresholds for verdict determination.

    Attributes:
        approval: Minimum score required for approval (default: 0.70)
        escalation: Minimum score for force approval at max iterations (default: 0.50)
    """

    approval: float = 0.70
    escalation: float = 0.50


class QualityConfig:
    """Quality configuration with default and node-specific thresholds.

    Provides configurable quality thresholds that can be customized per node type.
    Supports loading from configuration files or using code defaults.

    Attributes:
        default_thresholds: Default thresholds for all nodes
        node_overrides: Node-specific threshold overrides
    """

    # Default thresholds for unknown nodes
    DEFAULT_APPROVAL = 0.70
    DEFAULT_ESCALATION = 0.50

    # Stricter thresholds for architect node
    ARCHITECT_APPROVAL = 0.75
    ARCHITECT_ESCALATION = 0.55

    def __init__(
        self,
        default_thresholds: QualityThresholds | None = None,
        node_overrides: dict[str, QualityThresholds] | None = None,
    ):
        """Initialize QualityConfig.

        Args:
            default_thresholds: Custom default thresholds (default: 0.70/0.50)
            node_overrides: Dictionary of node-specific threshold overrides
        """
        self.default_thresholds = default_thresholds or QualityThresholds()
        self.node_overrides = node_overrides or {}

    def get_thresholds(self, node_id: str) -> QualityThresholds:
        """Get thresholds for a specific node.

        Args:
            node_id: The node identifier (e.g., 'architect', 'reviewer')

        Returns:
            QualityThresholds for the specified node
        """
        # Check for explicit node override first
        if node_id in self.node_overrides:
            return self.node_overrides[node_id]

        # Apply architect-specific stricter thresholds
        if node_id == "architect":
            return QualityThresholds(
                approval=self.ARCHITECT_APPROVAL,
                escalation=self.ARCHITECT_ESCALATION,
            )

        # Return default thresholds
        return self.default_thresholds


class VerdictDeterminer:
    """Determines verdict based on alignment score and thresholds.

    Uses QualityConfig to determine the appropriate verdict for a node
    based on the alignment score, current iteration, and maximum iterations.
    """

    def __init__(self, config: QualityConfig):
        """Initialize VerdictDeterminer.

        Args:
            config: QualityConfig instance with threshold settings
        """
        self.config = config

    def determine_verdict(
        self,
        alignment_score: float,
        node_id: str,
        iteration: int,
        max_iterations: int,
    ) -> Verdict:
        """Determine the verdict for a quality evaluation.

        Args:
            alignment_score: The alignment score to evaluate (0.0 to 1.0)
            node_id: The node identifier for threshold lookup
            iteration: Current iteration number (1-indexed)
            max_iterations: Maximum allowed iterations

        Returns:
            Verdict based on score and iteration status
        """
        thresholds = self.config.get_thresholds(node_id)

        # At max iterations, use escalation threshold
        if iteration >= max_iterations:
            if alignment_score >= thresholds.escalation:
                return Verdict.FORCE_APPROVED
            else:
                return Verdict.BLOCKED

        # Before max iterations, use approval threshold
        if alignment_score >= thresholds.approval:
            return Verdict.APPROVED
        else:
            return Verdict.NEEDS_REVISION

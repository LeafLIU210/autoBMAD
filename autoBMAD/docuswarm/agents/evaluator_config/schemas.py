"""Evaluation Criteria Schema Definitions - Story 2.8.

This module provides TypedDict definitions for:
- CriteriaWeights: Single criterion weight configuration
- EvaluationCriteria: Full evaluation criteria with universal defaults and node overrides
- ThresholdConfig: Approval/escalation threshold configuration
- EVALUATOR_OUTPUT_SCHEMA: JSON Schema for SDK structured output (Story 38.1)
"""

from typing import Any, TypedDict


class CriteriaWeights(TypedDict):
    """Single criterion weight configuration.

    Attributes:
        name: Unique identifier for the criterion.
        description: Human-readable description of what the criterion evaluates.
        weight: Numeric weight (0.0-1.0) for this criterion.
    """

    name: str
    description: str
    weight: float


class ThresholdConfig(TypedDict, total=False):
    """Threshold configuration for verdict determination.

    Attributes:
        approval: Minimum alignment score for APPROVED verdict (default 0.70).
        escalation: Maximum alignment score for BLOCKED verdict (default 0.50).
    """

    approval: float
    escalation: float


class EvaluationCriteria(TypedDict, total=False):
    """Full evaluation criteria configuration.

    This TypedDict defines:
    - Universal/default criteria weights that apply to all nodes
    - Node-specific weight overrides for particular nodes
    - Threshold configuration for verdict determination
    - Optional node-specific criteria beyond the universal set

    Attributes:
        universal_weights: Default criteria weights applied to all nodes.
            Default: completeness: 0.30, clarity: 0.20, consistency: 0.20,
            actionability: 0.20, evidence_quality: 0.10
        node_overrides: Node-specific weight overrides.
            Keys are node_id strings, values are dicts of criterion name to weight.
        thresholds: Threshold configuration for verdict determination.
        node_specific_criteria: Additional criteria specific to certain nodes.
    """

    universal_weights: dict[str, float]
    node_overrides: dict[str, dict[str, float]]
    thresholds: ThresholdConfig
    node_specific_criteria: dict[str, list[CriteriaWeights]]


# Universal criteria defaults
UNIVERSAL_CRITERIA_DEFAULTS: dict[str, float] = {
    "completeness": 0.30,
    "clarity": 0.20,
    "consistency": 0.20,
    "actionability": 0.20,
    "evidence_quality": 0.10,
}

# Default thresholds
DEFAULT_THRESHOLDS: ThresholdConfig = {
    "approval": 0.70,
    "escalation": 0.50,
}

# Weight validation tolerance
WEIGHT_SUM_TOLERANCE: float = 0.05

# EvaluatorAgent output schema for SDK structured output (Story 38.1)
# This schema defines the JSON Schema format for constrained EvaluatorAgent output
EVALUATOR_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "criterion_scores": {
            "type": "object",
            "description": "Scores for each evaluation criterion (0.0-1.0)",
            "additionalProperties": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
            },
        },
        "alignment_score": {
            "type": "number",
            "description": "Weighted alignment score (0.0-1.0)",
            "minimum": 0.0,
            "maximum": 1.0,
        },
        "verdict": {
            "type": "string",
            "description": "Evaluation verdict",
            "enum": ["APPROVED", "NEEDS_REVISION", "BLOCKED"],
        },
        "issues_found": {
            "type": "array",
            "description": "List of issues found during evaluation",
            "items": {"type": "string"},
        },
        "suggestions": {
            "type": "array",
            "description": "List of suggestions for improvement",
            "items": {"type": "string"},
        },
    },
    "required": [
        "criterion_scores",
        "alignment_score",
        "verdict",
        "issues_found",
        "suggestions",
    ],
}


__all__ = [
    "CriteriaWeights",
    "EvaluationCriteria",
    "ThresholdConfig",
    "UNIVERSAL_CRITERIA_DEFAULTS",
    "DEFAULT_THRESHOLDS",
    "WEIGHT_SUM_TOLERANCE",
    "EVALUATOR_OUTPUT_SCHEMA",
]

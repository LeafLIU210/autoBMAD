# Evaluator Configuration Package - Story 2.8
"""Evaluator configuration module containing schemas and criteria loader."""

from autoBMAD.docuswarm.agents.evaluator_config.criteria_loader import (
    CriteriaLoader,
    CriteriaValidationError,
    load_criteria,
)
from autoBMAD.docuswarm.agents.evaluator_config.schemas import (
    DEFAULT_THRESHOLDS,
    UNIVERSAL_CRITERIA_DEFAULTS,
    WEIGHT_SUM_TOLERANCE,
    CriteriaWeights,
    EvaluationCriteria,
    ThresholdConfig,
)

__all__ = [
    "CriteriaLoader",
    "CriteriaValidationError",
    "load_criteria",
    "DEFAULT_THRESHOLDS",
    "EvaluationCriteria",
    "CriteriaWeights",
    "ThresholdConfig",
    "UNIVERSAL_CRITERIA_DEFAULTS",
    "WEIGHT_SUM_TOLERANCE",
]

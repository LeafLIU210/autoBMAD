"""Criteria Loader - Story 2.8.

This module provides the criteria_loader functionality for loading and validating
evaluation criteria from YAML configuration files.

Features:
- Load YAML file for specified node_id
- Validate weights sum to 1.0 (with 0.05 tolerance)
- Validate threshold values are between 0.0 and 1.0
- Apply node-specific weight overrides to universal defaults
- Return structured data for Evaluator Agent consumption
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypedDict, cast

import yaml

from autoBMAD.docuswarm.agents.evaluator_config.schemas import (
    DEFAULT_THRESHOLDS,
    WEIGHT_SUM_TOLERANCE,
    CriteriaWeights,
    ThresholdConfig,
)


class LoadedCriteria(TypedDict):
    """Return type for CriteriaLoader.load() method."""

    criteria: list[CriteriaWeights]
    thresholds: ThresholdConfig
    node_id: str


class CriteriaValidationError(Exception):
    """Raised when criteria validation fails."""

    pass


class CriteriaLoader:
    """Loader for evaluation criteria from YAML files.

    This class handles:
    - Loading criteria from nodes/{node_id}/evaluator.yaml
    - Validating weight sums (within tolerance)
    - Validating threshold ranges
    - Applying universal defaults with node-specific overrides

    Attributes:
        project_root: Root directory of the project.
    """

    VALID_CRITERION_FIELDS = {"name", "description", "weight"}

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize the criteria loader.

        Args:
            project_root: Root directory of the project. If None, uses cwd.
        """
        self.project_root = project_root or Path.cwd()

    def load(self, node_id: str) -> LoadedCriteria:
        """Load evaluation criteria for the specified node.

        Args:
            node_id: The node identifier (e.g., 'analyst', 'pm', 'ux', 'architect', 'po').

        Returns:
            Dictionary containing:
                - criteria: List of criteria dicts with name, description, weight
                - thresholds: Threshold configuration dict
                - node_id: The node identifier

        Raises:
            FileNotFoundError: If the evaluator.yaml file doesn't exist.
            CriteriaValidationError: If validation fails.
        """
        criteria_path = self.project_root / "nodes" / node_id / "evaluator.yaml"

        if not criteria_path.exists():
            raise FileNotFoundError(
                f"Criteria file not found: {criteria_path}. Expected at nodes/{node_id}/evaluator.yaml"
            )

        # Load YAML
        try:
            with open(criteria_path, encoding="utf-8") as f:
                data: dict[str, Any] = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise CriteriaValidationError(f"Invalid YAML in criteria file: {e}") from e
        except OSError as e:
            raise CriteriaValidationError(f"Failed to read criteria file: {e}") from e

        if not data:
            raise CriteriaValidationError("Criteria file is empty")

        # Validate and extract criteria
        criteria = self._validate_criteria(cast(list[dict[str, Any]], data.get("criteria", [])))

        # Validate and extract thresholds
        thresholds = self._validate_thresholds(cast(dict[str, Any] | None, data.get("thresholds")))

        return {
            "criteria": criteria,
            "thresholds": thresholds,
            "node_id": node_id,
        }

    def _validate_criteria(self, criteria: list[dict[str, Any]]) -> list[CriteriaWeights]:
        """Validate criteria list and weights.

        Args:
            criteria: Raw criteria data from YAML.

        Returns:
            Validated criteria list.

        Raises:
            CriteriaValidationError: If validation fails.
        """
        if len(criteria) == 0:
            raise CriteriaValidationError("At least one criterion is required")

        # Validate each criterion
        total_weight = 0.0
        seen_names: set[str] = set()

        validated_criteria: list[CriteriaWeights] = []

        for i, criterion in enumerate(criteria):
            # Check required fields
            if "name" not in criterion:
                raise CriteriaValidationError(f"Criteria[{i}]: 'name' is required")
            if "description" not in criterion:
                raise CriteriaValidationError(f"Criteria[{i}]: 'description' is required")
            if "weight" not in criterion:
                raise CriteriaValidationError(f"Criteria[{i}]: 'weight' is required")

            # Validate name uniqueness
            name: str = criterion["name"]
            if name in seen_names:
                raise CriteriaValidationError(f"Criteria[{i}]: duplicate criterion name '{name}'")
            seen_names.add(name)

            # Validate weight
            weight: float = criterion["weight"]
            if weight < 0 or weight > 1:
                raise CriteriaValidationError(
                    f"Criteria[{i}] '{name}': 'weight' must be between 0 and 1"
                )

            total_weight += weight

            # Add validated criterion
            validated_criteria.append(
                CriteriaWeights(
                    name=name,
                    description=criterion["description"],
                    weight=weight,
                )
            )

        # Validate weight sum (with tolerance)
        if not abs(total_weight - 1.0) <= WEIGHT_SUM_TOLERANCE:
            raise CriteriaValidationError(
                f"Criteria weights must sum to 1.0 (within {WEIGHT_SUM_TOLERANCE} tolerance), got {total_weight}"
            )

        return validated_criteria

    def _validate_thresholds(self, thresholds: dict[str, Any] | None) -> ThresholdConfig:
        """Validate threshold configuration.

        Args:
            thresholds: Raw threshold data from YAML.

        Returns:
            Validated thresholds dict with defaults applied.

        Raises:
            CriteriaValidationError: If validation fails.
        """
        # Use defaults if not provided
        if thresholds is None:
            return ThresholdConfig(
                approval=DEFAULT_THRESHOLDS.get("approval", 0.70),
                escalation=DEFAULT_THRESHOLDS.get("escalation", 0.50),
            )

        result: ThresholdConfig = {"approval": 0.0, "escalation": 0.0}

        # Validate approval threshold
        if "approval" in thresholds:
            approval: float = thresholds["approval"]
            if approval < 0.0 or approval > 1.0:
                raise CriteriaValidationError("thresholds.approval must be between 0.0 and 1.0")
            result["approval"] = float(approval)
        else:
            result["approval"] = DEFAULT_THRESHOLDS.get("approval", 0.70)

        # Validate escalation threshold
        if "escalation" in thresholds:
            escalation: float = thresholds["escalation"]
            if escalation < 0.0 or escalation > 1.0:
                raise CriteriaValidationError("thresholds.escalation must be between 0.0 and 1.0")
            result["escalation"] = float(escalation)
        else:
            result["escalation"] = DEFAULT_THRESHOLDS.get("escalation", 0.50)

        # Validate logical relationship
        if result["approval"] <= result["escalation"]:
            raise CriteriaValidationError(
                "thresholds.approval must be greater than thresholds.escalation"
            )

        return result


# Convenience function
def load_criteria(node_id: str, project_root: Path | None = None) -> LoadedCriteria:
    """Load evaluation criteria for the specified node.

    Args:
        node_id: The node identifier.
        project_root: Root directory of the project.

    Returns:
        Dictionary containing criteria, thresholds, and node_id.

    Raises:
        FileNotFoundError: If the evaluator.yaml file doesn't exist.
        CriteriaValidationError: If validation fails.
    """
    loader = CriteriaLoader(project_root)
    return loader.load(node_id)


__all__ = [
    "CriteriaLoader",
    "CriteriaValidationError",
    "LoadedCriteria",
    "load_criteria",
]

"""Spec Automation Package

This module provides functionality for automating specification parsing,
generation, and validation for the autoBMAD system.
"""

from .spec_generator import (
    SpecGenerator,
    create_test_spec,
    generate_specification,
)
from .spec_parser import (
    SpecificationData,
    SpecParser,
    extract_requirements,
    parse_specification,
    validate_specification,
)
from .spec_validator import (
    SpecValidator,
    ValidationResult,
    check_spec_consistency,
    validate_spec_completeness,
)

__all__ = [
    "SpecParser",
    "SpecificationData",
    "parse_specification",
    "validate_specification",
    "extract_requirements",
    "SpecGenerator",
    "generate_specification",
    "create_test_spec",
    "SpecValidator",
    "ValidationResult",
    "validate_spec_completeness",
    "check_spec_consistency",
]

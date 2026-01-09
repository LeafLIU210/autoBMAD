"""Specification validation functionality."""

from dataclasses import dataclass

from autoBMAD.spec_automation.spec_parser import SpecificationData


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]

    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)

    def __str__(self) -> str:
        """String representation of the validation result."""
        result = f"Valid: {self.is_valid}\n"
        if self.errors:
            result += f"Errors ({len(self.errors)}):\n"
            for error in self.errors:
                result += f"  - {error}\n"
        if self.warnings:
            result += f"Warnings ({len(self.warnings)}):\n"
            for warning in self.warnings:
                result += f"  - {warning}\n"
        return result


class SpecValidator:
    """Validator for specification documents."""

    def __init__(self) -> None:
        """Initialize the validator."""
        pass

    def validate(self, spec: SpecificationData) -> ValidationResult:
        """Validate a specification.

        Args:
            spec: The specification to validate

        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        # Check required fields
        if not spec.name or not spec.name.strip():
            result.add_error("Specification name is required")

        if not spec.version or not spec.version.strip():
            result.add_error("Specification version is required")

        if not spec.description or not spec.description.strip():
            result.add_warning("Specification description is recommended")

        # Validate name format
        if spec.name and len(spec.name.strip()) < 3:
            result.add_warning("Specification name is quite short")

        # Validate version format (simple check)
        if spec.version:
            import re

            version_pattern = r"^\d+\.\d+(\.\d+)?$"
            if not re.match(version_pattern, spec.version):
                result.add_warning(
                    "Version should follow semantic versioning (e.g., 1.0.0)"
                )

        # Check requirements
        if not spec.requirements:
            result.add_warning("Specification should have at least one requirement")
        elif len(spec.requirements) < 2:
            result.add_warning("Consider adding more detailed requirements")

        # Validate requirement quality
        for i, req in enumerate(spec.requirements):
            if len(req.strip()) < 10:
                result.add_warning(
                    f"Requirement {i + 1} is very brief, consider adding more detail"
                )

        return result

    def check_completeness(self, spec: SpecificationData) -> float:
        """Check the completeness of a specification.

        Args:
            spec: The specification to check

        Returns:
            Completeness score between 0.0 and 1.0
        """
        score = 0.0

        # Name contributes 20%
        if spec.name and len(spec.name.strip()) >= 3:
            score += 0.2

        # Version contributes 20%
        if spec.version and len(spec.version.strip()) >= 1:
            score += 0.2

        # Description contributes 30%
        if spec.description and len(spec.description.strip()) >= 20:
            score += 0.3
        elif spec.description:
            score += 0.15

        # Requirements contribute 30%
        if spec.requirements:
            if len(spec.requirements) >= 3:
                score += 0.3
            elif len(spec.requirements) >= 1:
                score += 0.2

        return score

    def check_consistency(self, spec: SpecificationData) -> bool:
        """Check the consistency of a specification.

        Args:
            spec: The specification to check

        Returns:
            True if consistent, False otherwise
        """
        # Check for duplicate requirements
        if len(spec.requirements) != len(set(spec.requirements)):
            return False

        # Check for very short requirements (likely placeholders)
        for req in spec.requirements:
            if len(req.strip()) < 3:
                return False

        return True

    def validate_requirements(self, requirements: list[str]) -> ValidationResult:
        """Validate a list of requirements.

        Args:
            requirements: The list of requirements to validate

        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True, errors=[], warnings=[])

        if not requirements:
            result.add_error("Requirements list cannot be empty")
            return result

        # Check for duplicates
        if len(requirements) != len(set(requirements)):
            result.add_warning("Duplicate requirements found")

        # Check requirement quality
        for i, req in enumerate(requirements):
            if len(req.strip()) < 5:
                result.add_warning(f"Requirement {i + 1} is very short: '{req}'")

        return result


def validate_spec_completeness(spec: SpecificationData) -> float:
    """Validate the completeness of a specification.

    Args:
        spec: The specification to validate

    Returns:
        Completeness score between 0.0 and 1.0
    """
    validator = SpecValidator()
    return validator.check_completeness(spec)


def check_spec_consistency(spec: SpecificationData) -> bool:
    """Check the consistency of a specification.

    Args:
        spec: The specification to check

    Returns:
        True if consistent, False otherwise
    """
    validator = SpecValidator()
    return validator.check_consistency(spec)

"""Template validator for prompt isolation - Story 4.5.

This module provides validation to ensure proper context isolation between
Independent and Evaluator agent templates.
"""

import structlog
from structlog import BoundLogger

# Configure module logger
logger: BoundLogger = structlog.get_logger(__name__)


class TemplateIsolationError(Exception):
    """Raised when template isolation validation fails."""

    pass


class TemplateValidator:
    """Validates that templates maintain proper context isolation.

    The validator ensures that Evaluator templates do NOT contain any
    reference to private fields from the Independent Agent template,
    enforcing context isolation at the prompt level.
    """

    # Fields that should NOT appear in Evaluator template
    FORBIDDEN_FIELDS: list[str] = [
        "private_reasoning",
        "internal_notes",
        "tool_call_history",
        "iteration_feedback",
    ]

    def validate_isolation(self, independent_template: str, evaluator_template: str) -> bool:
        """Validate that Evaluator template does not contain forbidden fields.

        Args:
            independent_template: The Independent Agent template string.
            evaluator_template: The Evaluator Agent template string.

        Returns:
            True if validation passes.

        Raises:
            TemplateIsolationError: If forbidden fields are found in evaluator template.
        """
        logger.info(
            "validating_template_isolation",
            independent_length=len(independent_template),
            evaluator_length=len(evaluator_template),
        )

        # Check each forbidden field
        for field in self.FORBIDDEN_FIELDS:
            if field.lower() in evaluator_template.lower():
                error_msg = (
                    f"Template isolation violation: Evaluator template contains "
                    f"forbidden field '{field}'. This field should only exist "
                    f"in the Independent Agent template."
                )
                logger.error("template_isolation_violation", field=field)
                raise TemplateIsolationError(error_msg)

        logger.info("template_isolation_validated", status="pass")
        return True

    def check_field_in_template(self, template: str, field: str) -> bool:
        """Check if a field exists in a template.

        Args:
            template: The template string to check.
            field: The field name to search for.

        Returns:
            True if field is found in template.
        """
        return field.lower() in template.lower()

    def get_forbidden_fields_in_template(self, template: str) -> list[str]:
        """Get list of forbidden fields present in a template.

        Args:
            template: The template string to check.

        Returns:
            List of forbidden fields found in the template.
        """
        found = []
        for field in self.FORBIDDEN_FIELDS:
            if field.lower() in template.lower():
                found.append(field)
        return found

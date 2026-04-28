"""Template loader for prompt templates - Story 4.5.

This module provides the TemplateLoader class for loading and rendering
YAML-based prompt templates with variable substitution and validation.
"""

import re
from pathlib import Path
from typing import Any

import structlog
import yaml
from pydantic import BaseModel, Field, ValidationError

from autoBMAD.docuswarm.prompts.validator import (
    TemplateValidator,
)

# Configure module logger
logger = structlog.get_logger(__name__)


class PlaceholderDefinition(BaseModel):
    """Model for placeholder definition in template metadata."""

    type: str = Field(..., description="Type of the placeholder (string, integer, etc.)")
    description: str = Field(..., description="Description of the placeholder")
    required: bool = Field(default=True, description="Whether this placeholder is required")
    enum: list[str] | None = Field(default=None, description="Allowed values if enum")


class OutputFieldDefinition(BaseModel):
    """Model for output field definition in template metadata."""

    name: str = Field(..., description="Name of the output field")
    type: str = Field(..., description="Type of the output field")
    description: str = Field(..., description="Description of the field")
    required: bool = Field(default=True, description="Whether this field is required")
    enum: list[str] | None = Field(default=None, description="Allowed values if enum")
    range: list[int] | None = Field(default=None, description="Valid range if numeric")


class TemplateMetadata(BaseModel):
    """Model for template metadata loaded from YAML."""

    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    version: str = Field(..., description="Template version")
    placeholders: dict[str, PlaceholderDefinition] = Field(
        default_factory=dict, description="Placeholder definitions"
    )
    output_fields: list[OutputFieldDefinition] = Field(
        default_factory=list, description="Expected output fields"
    )
    forbidden_fields: list[str] = Field(
        default_factory=list, description="Fields that should not appear in this template"
    )


class TemplateLoadError(Exception):
    """Raised when template loading fails."""

    pass


class TemplateRenderError(Exception):
    """Raised when template rendering fails."""

    pass


class TemplateValidationError(Exception):
    """Raised when template validation fails."""

    pass


class TemplateLoader:
    """Loads and renders YAML-based prompt templates.

    This class provides functionality to:
    - Load templates from YAML files
    - Validate template structure
    - Substitute placeholder variables
    - Validate isolation between templates
    """

    # F8 Fix: Point to docuswarm/templates/ instead of prompts/templates/
    DEFAULT_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

    def __init__(self, templates_dir: Path | None = None):
        """Initialize the TemplateLoader.

        Args:
            templates_dir: Optional custom directory for templates.
                          Defaults to prompts/templates/
        """
        self.templates_dir = templates_dir or self.DEFAULT_TEMPLATES_DIR
        self._template_cache: dict[str, dict[str, Any]] = {}
        self._validator = TemplateValidator()
        logger.info("template_loader_initialized", templates_dir=str(self.templates_dir))

    def load_template(self, template_name: str) -> dict[str, Any]:
        """Load a template from YAML file.

        Args:
            template_name: Name of the template (without .yaml extension)

        Returns:
            Dictionary containing template metadata and content

        Raises:
            TemplateLoadError: If template file cannot be found or parsed
        """
        # Check cache first
        if template_name in self._template_cache:
            logger.debug("template_loaded_from_cache", template_name=template_name)
            return self._template_cache[template_name]

        template_path = self.templates_dir / f"{template_name}.yaml"

        if not template_path.exists():
            error_msg = f"Template not found: {template_path}"
            logger.error("template_not_found", path=str(template_path))
            raise TemplateLoadError(error_msg)

        try:
            with open(template_path, encoding="utf-8") as f:
                raw_template = yaml.safe_load(f)

            # Extract metadata and template content
            # Use explicit field values to trigger Pydantic validation
            placeholders_raw = raw_template.get("placeholders", {})
            output_fields_raw = raw_template.get("output_fields", [])
            template_content = raw_template.get("template", "")

            template_data = {
                "metadata": TemplateMetadata(
                    name=raw_template.get("name"),  # Will fail validation if missing
                    description=raw_template.get("description", ""),  # Optional with default
                    version=raw_template.get("version"),  # Will fail validation if missing
                    placeholders={
                        k: PlaceholderDefinition(**v) for k, v in placeholders_raw.items()
                    },
                    output_fields=[OutputFieldDefinition(**f) for f in output_fields_raw],
                    forbidden_fields=raw_template.get("forbidden_fields", []),
                ),
                "template_content": template_content,
                "raw": raw_template,
            }

            self._template_cache[template_name] = template_data
            logger.info("template_loaded", template_name=template_name)
            return template_data

        except yaml.YAMLError as e:
            error_msg = f"Failed to parse YAML template: {e}"
            logger.error("yaml_parse_error", template=template_name, error=str(e))
            raise TemplateLoadError(error_msg) from e
        except ValidationError as e:
            error_msg = f"Invalid template structure: {e}"
            logger.error("template_validation_error", template=template_name, error=str(e))
            raise TemplateLoadError(error_msg) from e

    def render_template(self, template_name: str, variables: dict[str, str]) -> str:
        """Render a template with variable substitution.

        Args:
            template_name: Name of the template to render
            variables: Dictionary of placeholder values

        Returns:
            Rendered template string

        Raises:
            TemplateRenderError: If required variables are missing or substitution fails
        """
        template_data = self.load_template(template_name)
        template_content = template_data["template_content"]

        # Validate required placeholders
        metadata = template_data["metadata"]
        missing_placeholders: list[str] = []
        for name, placeholder in metadata.placeholders.items():
            if placeholder.required and name not in variables:
                missing_placeholders.append(name)

        if missing_placeholders:
            error_msg = f"Missing required placeholders: {', '.join(missing_placeholders)}"
            logger.error("missing_placeholders", missing=missing_placeholders)
            raise TemplateRenderError(error_msg)

        # Perform variable substitution using {variable} syntax
        rendered = template_content
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            rendered = rendered.replace(placeholder, str(value))

        # Check for any unreplaced placeholders
        unreplaced = re.findall(r"\{(\w+)\}", rendered)
        if unreplaced:
            logger.warning("unreplaced_placeholders", placeholders=unreplaced)

        logger.info("template_rendered", template_name=template_name)
        return rendered

    def validate_template(self, template_name: str) -> bool:
        """Validate a template's structure and content.

        Args:
            template_name: Name of the template to validate

        Returns:
            True if validation passes

        Raises:
            TemplateValidationError: If validation fails
        """
        template_data = self.load_template(template_name)
        metadata = template_data["metadata"]

        # Check required metadata fields
        if not metadata.name:
            raise TemplateValidationError("Template must have a name")

        if not metadata.version:
            raise TemplateValidationError("Template must have a version")

        # Check that template content is not empty
        if not template_data["template_content"].strip():
            raise TemplateValidationError("Template content cannot be empty")

        # Validate placeholders have required fields
        for name, placeholder in metadata.placeholders.items():
            if not placeholder.description:
                logger.warning("placeholder_missing_description", placeholder=name)

        logger.info("template_validated", template_name=template_name)
        return True

    def validate_isolation(self, independent_template: str, evaluator_template: str) -> bool:
        """Validate that evaluator template doesn't contain forbidden fields.

        Args:
            independent_template: Name of the Independent Agent template
            evaluator_template: Name of the Evaluator Agent template

        Returns:
            True if isolation is maintained

        Raises:
            TemplateIsolationError: If isolation is violated
        """
        independent_data = self.load_template(independent_template)
        evaluator_data = self.load_template(evaluator_template)

        independent_content = independent_data["template_content"]
        evaluator_content = evaluator_data["template_content"]

        return self._validator.validate_isolation(independent_content, evaluator_content)

    def get_template_metadata(self, template_name: str) -> TemplateMetadata:
        """Get metadata for a template.

        Args:
            template_name: Name of the template

        Returns:
            TemplateMetadata object
        """
        template_data = self.load_template(template_name)
        return template_data["metadata"]

    def list_templates(self) -> list[str]:
        """List all available templates in the templates directory.

        Returns:
            List of template names (without .yaml extension)
        """
        if not self.templates_dir.exists():
            logger.warning("templates_dir_not_found", path=str(self.templates_dir))
            return []

        templates: list[str] = []
        for file_path in self.templates_dir.glob("*.yaml"):
            templates.append(file_path.stem)

        logger.debug("templates_listed", count=len(templates))
        return sorted(templates)

    def clear_cache(self) -> None:
        """Clear the template cache."""
        self._template_cache.clear()
        logger.info("template_cache_cleared")

"""Prompt templates module - Story 4.5.

This module contains separate prompt templates for Independent and Evaluator agents,
enforcing context isolation at the prompt level.
"""

from autoBMAD.docuswarm.prompts.evaluator_agent import TEMPLATE as EVALUATOR_TEMPLATE
from autoBMAD.docuswarm.prompts.independent_agent import (
    TEMPLATE as INDEPENDENT_TEMPLATE,
)
from autoBMAD.docuswarm.prompts.template_loader import (
    TemplateLoader,
    TemplateLoadError,
    TemplateRenderError,
    TemplateValidationError,
)
from autoBMAD.docuswarm.prompts.validator import (
    TemplateIsolationError,
    TemplateValidator,
)

__all__ = [
    "INDEPENDENT_TEMPLATE",
    "EVALUATOR_TEMPLATE",
    "TemplateValidator",
    "TemplateIsolationError",
    "TemplateLoader",
    "TemplateLoadError",
    "TemplateRenderError",
    "TemplateValidationError",
]

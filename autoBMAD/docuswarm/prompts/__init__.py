"""Prompt templates module - Story 4.5.

This module contains separate prompt templates for Independent and Evaluator agents,
enforcing context isolation at the prompt level.

P0: Node Prompt Contract Builder - Builds structured prompt contracts from
NodeExecutionContext for both Independent and Evaluator agents.
"""

from autoBMAD.docuswarm.prompts.contract_builder import (
    EvaluatorPromptContract,
    IndependentPromptContract,
    NodePromptContractBuilder,
    create_contract_builder,
)
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
    # P0: Node Prompt Contract Builder
    "NodePromptContractBuilder",
    "IndependentPromptContract",
    "EvaluatorPromptContract",
    "create_contract_builder",
    # Legacy templates
    "INDEPENDENT_TEMPLATE",
    "EVALUATOR_TEMPLATE",
    "TemplateValidator",
    "TemplateIsolationError",
    "TemplateLoader",
    "TemplateLoadError",
    "TemplateRenderError",
    "TemplateValidationError",
]

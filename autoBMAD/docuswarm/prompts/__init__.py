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
from autoBMAD.docuswarm.prompts.skill_injector import (
    NODE_SKILL_MAP,
    SkillInjector,
)
from autoBMAD.docuswarm.prompts.template_engine import (
    PromptBuildConfig,
    PromptTemplateEngine,
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
    # Story 29.6: Four-Layer Prompt Architecture
    "PromptBuildConfig",
    "PromptTemplateEngine",
    # P0: Node Prompt Contract Builder
    "NodePromptContractBuilder",
    "IndependentPromptContract",
    "EvaluatorPromptContract",
    "create_contract_builder",
    # Story 29.5: BMAD Skill Injector
    "SkillInjector",
    "NODE_SKILL_MAP",
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

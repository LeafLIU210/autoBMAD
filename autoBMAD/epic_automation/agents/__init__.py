"""
Agents - Agent 层

Agent 负责业务逻辑实现，Prompt 构造，结果解释。
"""

# Import anthropic for test mocking
try:
    import anthropic
    Anthropic = anthropic.Anthropic
except Exception:
    anthropic = None
    Anthropic = None

from autoBMAD.epic_automation.agents.base_agent import BaseAgent
from autoBMAD.epic_automation.agents.sm_agent import SMAgent
from autoBMAD.epic_automation.agents.state_agent import StateAgent
from autoBMAD.epic_automation.agents.dev_agent import DevAgent
from autoBMAD.epic_automation.agents.qa_agent import QAAgent
from autoBMAD.epic_automation.agents.quality_agents import (
    BaseQualityAgent,
    RuffAgent,
    BasedPyrightAgent,
    PytestAgent
)
from autoBMAD.epic_automation.agents.config import (
    AgentConfig,
    DevConfig,
    SMConfig,
    QAConfig,
    QAResult,
)

__all__ = [
    'BaseAgent',
    'SMAgent',
    'StateAgent',
    'DevAgent',
    'QAAgent',
    'BaseQualityAgent',
    'RuffAgent',
    'BasedPyrightAgent',
    'PytestAgent',
    'AgentConfig',
    'DevConfig',
    'SMConfig',
    'QAConfig',
    'QAResult',
    'Anthropic',
]

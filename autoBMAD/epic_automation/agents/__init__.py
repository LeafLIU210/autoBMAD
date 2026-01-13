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

from .base_agent import BaseAgent
from .sm_agent import SMAgent
from .state_agent import StateAgent
from .dev_agent import DevAgent
from .qa_agent import QAAgent
from .quality_agents import (
    BaseQualityAgent,
    RuffAgent,
    BasedPyrightAgent,
    PytestAgent
)
from .config import (
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

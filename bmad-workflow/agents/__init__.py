"""
BMAD Agents Package

This package contains the SM, Dev, and QA agents for the BMAD
(Breakthrough Method of Agile AI-driven Development) automation system.

Agents:
    - BaseAgent: Shared base class with common functionality
    - SMAgent: Story creation and preparation
    - DevAgent: Story implementation and development
    - QAAgent: Quality assessment and gate decisions

Each agent loads its corresponding task guidance from .bmad-core/tasks/
and creates fresh Claude SDK clients per session.
"""

from .base_agent import BaseAgent
from .sm_agent import SMAgent
from .dev_agent import DevAgent
from .qa_agent import QAAgent, QAResultStatus, QAGateResult

__all__ = [
    'BaseAgent',
    'SMAgent',
    'DevAgent',
    'QAAgent',
    'QAResultStatus',
    'QAGateResult'
]

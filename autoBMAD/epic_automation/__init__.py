"""Epic Automation Package"""

from autoBMAD.epic_automation.agents.base_agent import BaseAgent
from autoBMAD.epic_automation.agents.config import (
    AgentConfig,
    DevConfig,
    QAConfig,
    QAResult,
    SMConfig,
)
from autoBMAD.epic_automation.agents.dev_agent import DevAgent

# EpicDriver is CLI entry, should not be imported in package __init__
# from autoBMAD.epic_automation.epic_driver import EpicDriver
from autoBMAD.epic_automation.agents.qa_agent import QAAgent
from autoBMAD.epic_automation.agents.quality_agents import (
    BasedPyrightAgent,
    BaseQualityAgent,
    PytestAgent,
    RuffAgent,
)
from autoBMAD.epic_automation.agents.sm_agent import SMAgent

# 导出 core 组件
from autoBMAD.epic_automation.core import (
    CancellationManager,
    SDKErrorType,
    SDKExecutor,
    SDKResult,
)
from autoBMAD.epic_automation.state_manager import StateManager

__all__ = [
    # 旧版组件
    "SMAgent",
    "StateManager",
    # "EpicDriver",  # Removed: CLI entry should not be in package API
    "DevAgent",
    "QAAgent",
    "BaseQualityAgent",
    "RuffAgent",
    "BasedPyrightAgent",
    "PytestAgent",
    "BaseAgent",
    # Config classes
    "AgentConfig",
    "DevConfig",
    "SMConfig",
    "QAConfig",
    "QAResult",
    # Core 组件
    "SDKResult",
    "SDKErrorType",
    "SDKExecutor",
    "CancellationManager",
]

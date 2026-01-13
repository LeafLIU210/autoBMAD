"""Epic Automation Package"""

from .agents.base_agent import BaseAgent
from .agents.dev_agent import DevAgent
from .epic_driver import EpicDriver
from .agents.qa_agent import QAAgent
from .agents.quality_agents import (
    BaseQualityAgent,
    RuffAgent,
    BasedPyrightAgent,
    PytestAgent,
)
from .agents.config import (
    AgentConfig,
    DevConfig,
    SMConfig,
    QAConfig,
    QAResult,
)
# from .qa_tools_integration import (
#     BasedPyrightWorkflowRunner,
#     FixtestWorkflowRunner,
#     QAAutomationWorkflow,
#     QAError,
# )
# from .sdk_session_manager import (
#     IsolatedSDKContext,
#     SDKErrorType,
#     SDKExecutionResult,
#     SDKSessionManager,
#     get_session_manager,
#     reset_session_manager,
# )
from .agents.sm_agent import SMAgent
from .state_manager import StateManager
# from .story_parser import (
#     CORE_STATUS_VALUES,
#     EpicData,
#     SimpleStatusParser,
#     SimpleStoryParser,
#     StatusParser,
#     StoryData,
#     core_status_to_processing,
#     is_core_status_valid,
# )

# 导出 core 组件
from .core import (
    SDKResult,
    SDKErrorType,
    SDKExecutor,
    CancellationManager,
)

__all__ = [
    # 旧版组件
    "SMAgent",
    "StateManager",
    "EpicDriver",
    "DevAgent",
    "QAAgent",
    "BaseQualityAgent",
    "RuffAgent",
    "BasedPyrightAgent",
    "PytestAgent",
    # "QAError",
    # "BasedPyrightWorkflowRunner",
    # "FixtestWorkflowRunner",
    # "QAAutomationWorkflow",
    "BaseAgent",
    # Config classes
    "AgentConfig",
    "DevConfig",
    "SMConfig",
    "QAConfig",
    "QAResult",
    # SDK Session Manager
    # "SDKSessionManager",
    # "SDKExecutionResult",
    # "SDKErrorType",
    # "IsolatedSDKContext",
    # "get_session_manager",
    # "reset_session_manager",
    # Story Parser
    # "SimpleStoryParser",
    # "StatusParser",
    # "SimpleStatusParser",
    # "StoryData",
    # "EpicData",
    # "core_status_to_processing",
    # "is_core_status_valid",
    # "CORE_STATUS_VALUES",
    # Core 组件
    "SDKResult",
    "SDKErrorType",
    "SDKExecutor",
    "CancellationManager",
]

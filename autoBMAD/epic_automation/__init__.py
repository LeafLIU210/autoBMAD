"""Epic Automation Package"""

import sys
import importlib.util

# 导入旧版组件（从 agents.py 文件）
# 使用 importlib.util 绕过 agents 目录
spec = importlib.util.spec_from_file_location("agents_module", __file__.replace("__init__.py", "agents.py"))
if spec is None:
    raise ImportError(f"Cannot load spec for agents module from {__file__}")
agents_module = importlib.util.module_from_spec(spec)
sys.modules["agents_module"] = agents_module
if spec.loader is None:
    raise ImportError("Spec loader is None")
spec.loader.exec_module(agents_module)

AgentConfig = agents_module.AgentConfig
BaseAgent = agents_module.BaseAgent
from .agents.dev_agent import DevAgent
from .epic_driver import EpicDriver
from .agents.qa_agent import QAAgent
from .qa_tools_integration import (
    BasedPyrightWorkflowRunner,
    FixtestWorkflowRunner,
    QAAutomationWorkflow,
    QAError,
)
from .sdk_session_manager import (
    IsolatedSDKContext,
    SDKErrorType,
    SDKExecutionResult,
    SDKSessionManager,
    get_session_manager,
    reset_session_manager,
)
from .agents.sm_agent import SMAgent
from .state_manager import StateManager
from .story_parser import (
    CORE_STATUS_VALUES,
    EpicData,
    SimpleStatusParser,
    SimpleStoryParser,
    StatusParser,
    StoryData,
    core_status_to_processing,
    is_core_status_valid,
)

__all__ = [
    # 旧版组件
    "SMAgent",
    "StateManager",
    "EpicDriver",
    "DevAgent",
    "QAAgent",
    "QAError",
    "BasedPyrightWorkflowRunner",
    "FixtestWorkflowRunner",
    "QAAutomationWorkflow",
    "BaseAgent",
    "AgentConfig",
    # SDK Session Manager
    "SDKSessionManager",
    "SDKExecutionResult",
    "SDKErrorType",
    "IsolatedSDKContext",
    "get_session_manager",
    "reset_session_manager",
    # Story Parser
    "SimpleStoryParser",
    "StatusParser",
    "SimpleStatusParser",
    "StoryData",
    "EpicData",
    "core_status_to_processing",
    "is_core_status_valid",
    "CORE_STATUS_VALUES",
]

"""
Configuration classes for all agents.
"""
from enum import Enum


class StoryStatus(Enum):
    """Story status enum."""
    DRAFT = "Draft"
    IN_PROGRESS = "In Progress"
    READY_FOR_REVIEW = "Ready for Review"
    COMPLETED = "Completed"
    BLOCKED = "Blocked"


class AgentConfig:
    """Configuration for BaseAgent."""

    def __init__(
        self,
        task_name: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: str | None = None,
    ):
        self.task_name = task_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model = model
        self.api_key = api_key


class DevConfig:
    """Configuration for DevAgent."""

    def __init__(
        self,
        task_name: str = "dev-task",
        use_claude: bool = True,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: str | None = None,
    ):
        self.task_name = task_name
        self.use_claude = use_claude
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model = model
        self.api_key = api_key


class SMConfig:
    """Configuration for SMAgent."""

    def __init__(
        self,
        task_name: str = "sm-task",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: str | None = None,
    ):
        self.task_name = task_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model = model
        self.api_key = api_key


class QAConfig:
    """Configuration for QAAgent."""

    def __init__(
        self,
        task_name: str = "qa-task",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: str | None = None,
    ):
        self.task_name = task_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model = model
        self.api_key = api_key


class QAResult:
    """Result class for QA operations."""

    def __init__(
        self,
        passed: bool,
        score: float = 0.0,
        details: str | None = None,
        suggestions: list[str] | None = None,
    ):
        self.passed = passed
        self.score = score
        self.details = details
        self.suggestions = suggestions or []

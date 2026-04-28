"""Base agent abstract class - Story 2.1, Updated for Story 7.3.

Provides an abstract base class for all DocuSwarm agents with:
- Abstract execute() method all subclasses must implement
- Common initialization with config, logger, and LLM client/session manager
- Session manager injection for dependency inversion (Story 7.3)
- Type hints throughout for static analysis
- _format_system_prompt() method with NotImplementedError
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import structlog
from structlog.stdlib import BoundLogger

from autoBMAD.docuswarm.llm.session_manager import SessionManager

if TYPE_CHECKING:
    from autoBMAD.docuswarm.config import Config as _Config

    AgentConfig = _Config
else:
    # Runtime import to avoid circular imports
    from autoBMAD.docuswarm.config import Config as AgentConfig


class BaseAgent(ABC):
    """Abstract base class for all DocuSwarm agents.

    This class provides common functionality for all agents including:
    - Configuration management via AgentConfig
    - Structured logging via structlog
    - Session manager injection for dependency inversion (Story 7.3)

    Subclasses must implement the execute() method.

    Attributes:
        config: Agent configuration object.
        session_manager: SessionManager for SDK interactions.
    """

    def __init__(
        self,
        config: AgentConfig,
        session_manager: SessionManager | None = None,
    ) -> None:
        """Initialize the BaseAgent with config and session manager.

        Args:
            config: Agent configuration object containing settings.
            session_manager: SessionManager for SDK interactions.
        """
        self.config = config
        self.session_manager: SessionManager | None = session_manager

        if session_manager is None:
            raise ValueError("session_manager must be provided")

        _logger = structlog.get_logger()
        self.logger: BoundLogger = _logger.bind(agent=self.__class__.__name__)

    @abstractmethod
    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute agent logic and return results.

        This method must be implemented by all subclasses.

        Args:
            context: Execution context containing input data and state.

        Returns:
            Dict containing the results of agent execution.
        """
        pass

    def _format_system_prompt(self) -> str:
        """Format system prompt with persona and instructions.

        Subclasses should override this method to provide their
        specific system prompt.

        Returns:
            Formatted system prompt string.

        Raises:
            NotImplementedError: If called on base class without override.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement _format_system_prompt()"
        )

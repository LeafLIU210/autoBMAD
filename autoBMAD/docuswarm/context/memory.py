"""Memory management module - Story 4.3.

Provides memory isolation for agents with three scopes:
- SHARED: Accessible by both Independent and Evaluator agents
- INDEPENDENT: Private to Independent agent only
- EVALUATOR: Private to Evaluator agent only
"""

from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class MemoryScope(Enum):
    """Enum representing memory access scopes."""

    SHARED = "shared"
    INDEPENDENT = "independent"
    EVALUATOR = "evaluator"


class MemoryManager:
    """Manages isolated memory scopes for agent context.

    Provides separate storage for shared memory (accessible by both agents),
    Independent-only memory, and Evaluator-only memory.
    """

    def __init__(self) -> None:
        """Initialize MemoryManager with separate memory dictionaries."""
        self._shared_memory: dict[str, Any] = {}
        self._independent_memory: dict[str, Any] = {}
        self._evaluator_memory: dict[str, Any] = {}

    def write(self, key: str, value: Any, scope: MemoryScope) -> None:
        """Write a value to the specified memory scope.

        Args:
            key: The memory key to store the value under.
            value: The value to store.
            scope: The memory scope to write to (SHARED, INDEPENDENT, or EVALUATOR).
        """
        if scope == MemoryScope.SHARED:
            self._shared_memory[key] = value
            logger.debug(
                "memory_write",
                key=key,
                scope=scope.value,
                memory_type="shared",
            )
        elif scope == MemoryScope.INDEPENDENT:
            self._independent_memory[key] = value
            logger.debug(
                "memory_write",
                key=key,
                scope=scope.value,
                memory_type="independent",
            )
        elif scope == MemoryScope.EVALUATOR:
            self._evaluator_memory[key] = value
            logger.debug(
                "memory_write",
                key=key,
                scope=scope.value,
                memory_type="evaluator",
            )

    def read(self, key: str, scope: MemoryScope) -> Any:
        """Read a value from the specified memory scope.

        Args:
            key: The memory key to read.
            scope: The memory scope to read from.

        Returns:
            The value stored at the key, or None if the key doesn't exist.
        """
        match scope:
            case MemoryScope.SHARED:
                value = self._shared_memory.get(key)
                logger.debug(
                    "memory_read",
                    key=key,
                    scope=scope.value,
                    memory_type="shared",
                    found=value is not None,
                )
                return value
            case MemoryScope.INDEPENDENT:
                value = self._independent_memory.get(key)
                logger.debug(
                    "memory_read",
                    key=key,
                    scope=scope.value,
                    memory_type="independent",
                    found=value is not None,
                )
                return value
            case MemoryScope.EVALUATOR:
                value = self._evaluator_memory.get(key)
                logger.debug(
                    "memory_read",
                    key=key,
                    scope=scope.value,
                    memory_type="evaluator",
                    found=value is not None,
                )
                return value

    def get_agent_context(self, agent_type: str) -> dict[str, Any]:
        """Get combined memory context for an agent.

        Returns shared memory plus the agent-specific private memory.
        Independent agents get shared + independent memory.
        Evaluator agents get shared + evaluator memory.

        Args:
            agent_type: The type of agent ("independent" or "evaluator").

        Returns:
            Dictionary containing combined shared and agent-specific memory.
        """
        match agent_type:
            case "independent":
                context = {**self._shared_memory, **self._independent_memory}
                logger.debug(
                    "agent_context_retrieved",
                    agent_type=agent_type,
                    shared_keys=list(self._shared_memory.keys()),
                    private_keys=list(self._independent_memory.keys()),
                )
                return context
            case "evaluator":
                context = {**self._shared_memory, **self._evaluator_memory}
                logger.debug(
                    "agent_context_retrieved",
                    agent_type=agent_type,
                    shared_keys=list(self._shared_memory.keys()),
                    private_keys=list(self._evaluator_memory.keys()),
                )
                return context
            case _:
                logger.warning("unknown_agent_type", agent_type=agent_type)
                return {**self._shared_memory}

    def clear_private_memory(self, scope: MemoryScope) -> None:
        """Clear memory for the specified private scope.

        Does NOT affect shared memory - only clears the specified private scope.

        Args:
            scope: The private memory scope to clear (INDEPENDENT or EVALUATOR).
        """
        if scope == MemoryScope.INDEPENDENT:
            cleared_keys = list(self._independent_memory.keys())
            self._independent_memory.clear()
            logger.info(
                "memory_cleared",
                scope=scope.value,
                cleared_keys=cleared_keys,
            )
        elif scope == MemoryScope.EVALUATOR:
            cleared_keys = list(self._evaluator_memory.keys())
            self._evaluator_memory.clear()
            logger.info(
                "memory_cleared",
                scope=scope.value,
                cleared_keys=cleared_keys,
            )
        else:
            logger.warning(
                "clear_shared_memory_attempted",
                scope=scope.value,
                message="Cannot clear shared memory via clear_private_memory",
            )

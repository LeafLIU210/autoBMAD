"""Protocol definitions for tool dependencies."""

from typing import Any, Protocol


class OutputHandler(Protocol):
    """Protocol for output handler that saves deliverables."""

    async def save_deliverable(
        self,
        title: str,
        content: str,
        metadata: dict[str, Any],
    ) -> None:
        """Save a deliverable with title, content, and metadata."""
        ...

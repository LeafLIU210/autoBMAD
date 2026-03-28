"""Tool result definition for DocuSwarm."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    """Result of a tool execution."""

    success: bool
    result: Any = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "result": self.result,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolResult":
        """Create from dictionary."""
        return cls(
            success=data.get("success", False),
            result=data.get("result"),
            error=data.get("error"),
        )

    def __bool__(self) -> bool:
        """Return True if success."""
        return self.success

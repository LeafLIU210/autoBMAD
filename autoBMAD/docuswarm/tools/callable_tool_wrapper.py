"""Tool 包装器 - 内部 ToolResult 与 Claude SDK 的桥梁.

该模块提供统一的基类，让工具内部使用 ToolResult，
同时自动处理 SDK 边界转换。
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from autoBMAD.docuswarm.tools.sdk_adapter import adapt_to_claude
from autoBMAD.docuswarm.tools.tool_result import ToolResult

P = TypeVar("P", bound=BaseModel)


class ToolResultWrapper(Generic[P]):
    """Base class for tools that internally use ToolResult.

    Subclasses implement _execute() returning ToolResult,
    this wrapper handles SDK adaptation automatically.

    Example:
        class MyTool(ToolResultWrapper[MyParams]):
            name = "my_tool"
            description = "Does something"
            params: type[MyParams] = MyParams

            async def _execute(self, params: MyParams) -> ToolResult:
                # 内部逻辑返回 ToolResult
                return ToolResult(success=True, result={"data": "value"})
    """

    name: str = ""
    description: str = ""
    params: type[BaseModel] | None = None

    async def __call__(self, params: P) -> dict[str, Any]:
        """Execute tool and adapt result to SDK format.

        Args:
            params: Tool parameters

        Returns:
            SDK format dict
        """
        result = await self._execute(params)
        return adapt_to_claude(result)

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute tool and return SDK format result.

        This is an alias for __call__ for explicit execution.

        Args:
            params: Tool parameters as dict

        Returns:
            SDK format dict
        """
        # Convert dict to params model if needed
        if self.params is not None and isinstance(params, dict):
            params = self.params(**params)
        return await self(params)

    async def _execute(self, params: P) -> ToolResult:
        """Execute tool and return ToolResult.

        Subclasses must implement this method.

        Args:
            params: Tool parameters

        Returns:
            ToolResult with execution result

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(f"Subclass {self.__class__.__name__} must implement _execute()")


# Type aliases for backward compatibility
ToolResultCallableTool = ToolResultWrapper
CallableToolBase = ToolResultWrapper

__all__ = [
    "ToolResultWrapper",
    "ToolResultCallableTool",  # Backward compatibility
    "CallableToolBase",  # Backward compatibility
    "P",
]

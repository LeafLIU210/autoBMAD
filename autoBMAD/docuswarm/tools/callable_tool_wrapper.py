"""CallableTool2 包装器 - 内部 ToolResult 与 SDK 的桥梁.

该模块提供统一的基类，让工具内部使用 ToolResult，
同时自动处理 SDK 边界转换。
"""

from __future__ import annotations

from typing import Generic, TypeVar

from kimi_agent_sdk import CallableTool2, ToolReturnValue
from pydantic import BaseModel
from typing_extensions import override

from autoBMAD.docuswarm.tools.sdk_adapter import adapt_to_sdk
from autoBMAD.docuswarm.tools.tool_result import ToolResult

P = TypeVar("P", bound=BaseModel)


class ToolResultCallableTool(CallableTool2[P], Generic[P]):
    """Base class for tools that internally use ToolResult.

    Subclasses implement _execute() returning ToolResult,
    this wrapper handles SDK adaptation automatically.

    Example:
        class MyTool(ToolResultCallableTool[MyParams]):
            name = "my_tool"
            description = "Does something"
            params = MyParams

            async def _execute(self, params: MyParams) -> ToolResult:
                # 内部逻辑返回 ToolResult
                return ToolResult(success=True, result={"data": "value"})
    """

    @override
    async def __call__(self, params: P) -> ToolReturnValue:
        """Execute tool and adapt result to SDK format.

        Args:
            params: Tool parameters

        Returns:
            SDK ToolReturnValue
        """
        result = await self._execute(params)
        return adapt_to_sdk(result)

    async def _execute(self, _params: P) -> ToolResult:
        """Execute tool and return ToolResult.

        Subclasses must implement this method.

        Args:
            _params: Tool parameters

        Returns:
            ToolResult with execution result

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(f"Subclass {self.__class__.__name__} must implement _execute()")


# Type alias for backward compatibility
CallableToolBase = ToolResultCallableTool

__all__ = [
    "ToolResultCallableTool",
    "CallableToolBase",
    "P",
]

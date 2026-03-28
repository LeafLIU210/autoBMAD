"""SDK 边界适配层 - 将内部 ToolResult 转换为 SDK 所需格式.

该模块是 ToolResult 协议统一的唯一 SDK 适配点。所有工具内部返回 ToolResult，
仅在 SDK 边界通过此适配层转换为 ToolOk/ToolError。
"""

from __future__ import annotations

import json
from typing import Any

from kimi_agent_sdk import ToolError, ToolOk, ToolReturnValue

from autoBMAD.docuswarm.tools.tool_result import ToolResult


def adapt_to_sdk(result: ToolResult) -> ToolReturnValue:
    """将内部 ToolResult 转换为 SDK ToolReturnValue.

    这是唯一的 SDK 适配点，所有工具内部返回 ToolResult。

    Args:
        result: 内部 ToolResult 对象

    Returns:
        SDK ToolReturnValue (ToolOk 或 ToolError)

    Examples:
        >>> result = ToolResult(success=True, result={"key": "value"})
        >>> sdk_val = adapt_to_sdk(result)
        >>> isinstance(sdk_val, ToolOk)
        True
    """
    if result.success:
        # 将结构化结果序列化为 JSON 字符串
        output = (
            json.dumps(result.result, ensure_ascii=False, default=str)
            if result.result is not None
            else ""
        )
        return ToolOk(output=output)
    else:
        return ToolError(
            output="",
            message=result.error or "Unknown error",
            brief="Tool execution failed",
        )


def adapt_from_sdk(response: ToolReturnValue) -> ToolResult:
    """将 SDK 响应转换为内部 ToolResult.

    用于处理 SDK 返回的 ToolOk/ToolError。

    Args:
        response: SDK ToolReturnValue

    Returns:
        内部 ToolResult 对象

    Examples:
        >>> sdk_val = ToolOk(output='{"key": "value"}')
        >>> result = adapt_from_sdk(sdk_val)
        >>> result.success
        True
        >>> result.result
        {"key": "value"}
    """
    if isinstance(response, ToolOk):
        # 尝试解析 JSON 输出
        try:
            result = json.loads(response.output) if response.output else None
        except json.JSONDecodeError:
            # 如果不是有效 JSON，包装为结构化数据
            result = {"output": response.output}

        return ToolResult(success=True, result=result)

    elif isinstance(response, ToolError):
        return ToolResult(
            success=False,
            error=response.message,
        )

    else:
        return ToolResult(
            success=False,
            error=f"Unknown response type: {type(response)}",
        )


def adapt_result_to_metadata(result: ToolResult) -> dict[str, Any]:
    """从 ToolResult 提取 metadata 字典.

    用于需要访问结构化 metadata 的场景。

    Args:
        result: ToolResult 对象

    Returns:
        Metadata 字典
    """
    if not result.success:
        return {"error": result.error or "Unknown error"}

    if isinstance(result.result, dict):
        return result.result

    return {"result": result.result}


__all__ = [
    "adapt_to_sdk",
    "adapt_from_sdk",
    "adapt_result_to_metadata",
]

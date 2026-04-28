"""SDK 边界适配层 - 将内部 ToolResult 转换为 Claude SDK 所需格式.

该模块是 ToolResult 协议统一的唯一 SDK 适配点。所有工具内部返回 ToolResult，
仅在 SDK 边界通过此适配层转换为 Claude SDK 格式。
"""

from __future__ import annotations

import json
from typing import Any

from autoBMAD.docuswarm.tools.tool_result import ToolResult


def adapt_to_claude(result: ToolResult) -> dict[str, Any]:
    """将内部 ToolResult 转换为 Claude SDK 格式.

    这是唯一的 SDK 适配点，所有工具内部返回 ToolResult。

    Args:
        result: 内部 ToolResult 对象

    Returns:
        SDK 格式的 dict，包含 type, content, is_error 等字段

    Examples:
        >>> result = ToolResult(success=True, result={"key": "value"})
        >>> claude_dict = adapt_to_claude(result)
        >>> claude_dict["type"]
        'tool_result'
        >>> claude_dict["is_error"]
        False
    """
    if result.success:
        # 将结构化结果序列化为 JSON 字符串
        content = (
            json.dumps(result.result, ensure_ascii=False, default=str)
            if result.result is not None
            else ""
        )
        return {
            "type": "tool_result",
            "content": content,
            "is_error": False,
        }
    else:
        # 错误结果
        error_content = json.dumps(
            {
                "error": result.error or "Unknown error",
                "brief": "Tool execution failed",
            },
            ensure_ascii=False,
        )
        return {
            "type": "tool_result",
            "content": error_content,
            "is_error": True,
        }


def adapt_from_claude(response: dict[str, Any]) -> ToolResult:
    """将 Claude SDK 响应转换为内部 ToolResult.

    用于处理 Claude SDK 返回的工具结果。

    Args:
        response: Claude SDK 响应 dict

    Returns:
        内部 ToolResult 对象

    Examples:
        >>> response = {"type": "tool_result", "content": '{"key": "value"}'}
        >>> result = adapt_from_claude(response)
        >>> result.success
        True
    """
    if not isinstance(response, dict):
        return ToolResult(
            success=False,
            error=f"Expected dict response, got {type(response)}",
        )

    is_error = response.get("is_error", False)
    content = response.get("content", "")

    if is_error:
        # 尝试解析错误内容
        try:
            error_data = json.loads(content) if content else {}
            error_msg = error_data.get("error", content or "Unknown error")
        except json.JSONDecodeError:
            error_msg = content or "Unknown error"

        return ToolResult(
            success=False,
            error=error_msg,
        )

    # 成功结果 - 尝试解析 JSON 内容
    try:
        result = json.loads(content) if content else None
    except json.JSONDecodeError:
        # 如果不是有效 JSON，包装为结构化数据
        result = {"output": content}

    return ToolResult(success=True, result=result)


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
    "adapt_to_claude",
    "adapt_from_claude",
    "adapt_result_to_metadata",
]

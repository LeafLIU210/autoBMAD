"""Agent SDK 调用辅助模块

为Agent提供统一的SDK调用接口，封装SDKExecutor和SDKResult的使用。

使用方式:
    from .sdk_helper import execute_sdk_call

    result = await execute_sdk_call(
        prompt="Your prompt here",
        agent_name="SMAgent",
        timeout=1800.0
    )

    if result.is_success():
        # 处理成功
        pass
"""
import logging
from pathlib import Path
from typing import Any, TypedDict

from ..core.sdk_executor import SDKExecutor
from ..core.sdk_result import SDKResult, SDKErrorType

logger = logging.getLogger(__name__)

# SDK可用性检测
_sdk_available = False
try:
    from ..sdk_wrapper import SDK_AVAILABLE as _sdk_available
    from ..sdk_wrapper import ResultMessage
    from ..sdk_wrapper import query
except ImportError:
    ResultMessage = None
    query = None  # type: ignore[assignment]

# 使用导入的常量
SDK_AVAILABLE = _sdk_available


class SDKOptions(TypedDict):
    """SDK配置选项类型"""
    permission_mode: str
    cwd: str
    cli_path: str | None


class SDKNotAvailableError(Exception):
    """SDK不可用异常"""
    pass


def is_result_message(message: Any) -> bool:
    """检查是否为ResultMessage"""
    if ResultMessage is None:
        return False
    return isinstance(message, ResultMessage)


def is_error_result(message: Any) -> bool:
    """检查ResultMessage是否为错误"""
    if not is_result_message(message):
        return False
    return hasattr(message, "is_error") and message.is_error


def extract_result_content(message: Any) -> str | None:
    """提取ResultMessage的内容"""
    if not is_result_message(message):
        return None

    result = getattr(message, "result", None)
    if result is None:
        return None

    return str(result)


async def execute_sdk_call(
    prompt: str,
    agent_name: str,
    *,
    timeout: float | None = 1800.0,
    permission_mode: str = "bypassPermissions",
    cwd: str | None = None
) -> SDKResult:
    """
    执行SDK调用（Agent统一入口）

    Args:
        prompt: 提示词
        agent_name: Agent名称（用于日志）
        timeout: 超时时间（秒）
        permission_mode: 权限模式
        cwd: 工作目录

    Returns:
        SDKResult: 执行结果
    """
    # 检查SDK可用性
    if not SDK_AVAILABLE or query is None:
        logger.warning(f"[{agent_name}] Claude Agent SDK not available")
        return SDKResult(
            has_target_result=False,
            cleanup_completed=True,
            duration_seconds=0.0,
            session_id=f"{agent_name}-no-sdk",
            agent_name=agent_name,
            error_type=SDKErrorType.SDK_ERROR,
            errors=["Claude Agent SDK not installed"]
        )

    # 导入SDK类型
    try:
        from claude_agent_sdk import ClaudeAgentOptions  # type: ignore[import-untyped]
    except ImportError:
        logger.warning(f"[{agent_name}] Could not import ClaudeAgentOptions")
        return SDKResult(
            has_target_result=False,
            cleanup_completed=True,
            duration_seconds=0.0,
            session_id=f"{agent_name}-import-error",
            agent_name=agent_name,
            error_type=SDKErrorType.SDK_ERROR,
            errors=["Could not import ClaudeAgentOptions"]
        )

    # 创建SDK选项
    options = ClaudeAgentOptions(
        permission_mode=permission_mode,  # type: ignore[arg-type, reportArgumentType]
        cwd=cwd or str(Path.cwd())
    )

    # 创建SDK执行器
    executor = SDKExecutor()

    # 定义SDK函数工厂（返回异步生成器）
    async def sdk_func():
        """SDK调用函数"""
        assert query is not None, "query should not be None at this point"
        gen = query(prompt=prompt, options=options)
        async for message in gen:
            yield message

    # 定义目标检测函数
    def target_predicate(message: Any) -> bool:
        """检测是否为目标ResultMessage"""
        return is_result_message(message) and not is_error_result(message)

    # 执行SDK调用
    result = await executor.execute(
        sdk_func=sdk_func,
        target_predicate=target_predicate,
        timeout=timeout,
        agent_name=agent_name
    )

    # 日志记录
    if result.is_success():
        logger.info(
            f"[{agent_name}] SDK call succeeded "
            f"(duration: {result.duration_seconds:.2f}s)"
        )
    else:
        logger.warning(
            f"[{agent_name}] SDK call failed "
            f"(error_type: {result.error_type.value}, "
            f"errors: {result.errors})"
        )

    return result


def create_sdk_generator(
    prompt: str,
    options: Any | None = None
):
    """
    创建SDK异步生成器

    Args:
        prompt: 提示词
        options: Claude Agent选项

    Returns:
        AsyncIterator[Any]: SDK消息流生成器

    Raises:
        SDKNotAvailableError: 当SDK不可用时
    """
    if not SDK_AVAILABLE or query is None:
        raise SDKNotAvailableError(
            "claude-agent-sdk not installed. "
            "Install with: pip install claude-agent-sdk"
        )

    if options is None:
        try:
            from claude_agent_sdk import ClaudeAgentOptions  # type: ignore[import-untyped]
            options = ClaudeAgentOptions(
                permission_mode="bypassPermissions",  # type: ignore[arg-type, reportArgumentType]
                cwd=str(Path.cwd())
            )
        except ImportError:
            raise SDKNotAvailableError("Could not import ClaudeAgentOptions")

    return query(prompt=prompt, options=options)


def get_claude_cli_path() -> str | None:
    """
    获取当前虚拟环境中的Claude CLI可执行文件路径

    Returns:
        str | None: CLI路径，如果未找到则返回None
    """
    try:
        import claude_agent_sdk
        import os

        sdk_path = os.path.dirname(claude_agent_sdk.__file__)
        possible_paths = [
            os.path.join(sdk_path, "_bundled", "claude.exe"),  # Windows
            os.path.join(sdk_path, "_bundled", "claude"),      # Linux/macOS
            "claude"  # 如果在PATH中
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None  # 让SDK自动检测
    except Exception:
        return None


def get_sdk_options(**overrides: Any) -> dict[str, Any]:
    """
    获取统一的SDK配置选项

    Args:
        **overrides: 覆盖默认配置，如 permission_mode, timeout 等

    Returns:
        dict[str, Any]: SDK配置字典，包含所有必要参数
    """
    # 获取CLI路径
    cli_path = get_claude_cli_path()

    # 默认配置
    default_options: dict[str, Any] = {
        'permission_mode': 'bypassPermissions',
        'cwd': str(Path.cwd()),
    }

    # 添加CLI路径（如果找到）
    if cli_path:
        default_options['cli_path'] = cli_path

    # 合并覆盖参数
    default_options.update(overrides)

    return default_options

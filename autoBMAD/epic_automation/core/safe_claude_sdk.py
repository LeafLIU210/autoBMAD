"""SafeClaudeSDK - 安全的Claude SDK封装

该模块提供对Claude SDK的安全封装：
- SafeClaudeSDK: 安全的Claude SDK类

核心功能：
1. 提供异步生成器接口
2. 在独立TaskGroup中调用Claude SDK
3. 处理Claude SDK内部的TaskGroup
4. 优雅处理取消和错误
"""

import anyio
import logging
from typing import Any, AsyncIterator
from pathlib import Path


logger = logging.getLogger(__name__)

# 尝试导入Claude SDK
_sdk_available: bool = False  # 默认设置为False
try:
    from claude_agent_sdk import ClaudeAgentOptions, query
    _sdk_available = True
except ImportError:
    ClaudeAgentOptions = None
    query = None

# 导出为公开API
SDK_AVAILABLE: bool = _sdk_available


class SafeClaudeSDK:
    """
    SafeClaudeSDK安全封装器

    提供对Claude SDK的安全封装，确保：
    1. 异步生成器接口
    2. 独立TaskGroup执行
    3. 优雅的取消和错误处理

    注意：如果Claude SDK不可用，初始化时会抛出RuntimeError。
    """

    def __init__(
        self,
        prompt: str,
        options: Any | None = None,
        log_manager: Any | None = None
    ) -> None:
        """
        初始化SafeClaudeSDK

        Args:
            prompt: 提示词
            options: Claude SDK选项
            log_manager: 日志管理器

        Raises:
            RuntimeError: 如果Claude SDK不可用
        """
        if not SDK_AVAILABLE:
            raise RuntimeError(
                "Claude SDK not available. "
                "Please install claude-agent-sdk package."
            )

        self.prompt = prompt
        self.options = options or self._create_default_options()
        self.log_manager = log_manager

        logger.debug(f"SafeClaudeSDK initialized for prompt: {prompt[:50]}...")

    def _create_default_options(self) -> Any | None:
        """
        创建默认的Claude SDK选项

        Returns:
            Any | None: 默认选项，如果SDK不可用则返回None
        """
        if ClaudeAgentOptions is None:
            return None

        return ClaudeAgentOptions(
            permission_mode="bypassPermissions",
            cwd=str(Path.cwd())
        )

    async def execute(self) -> AsyncIterator[Any]:
        """
        执行SDK调用（异步生成器接口）

        Yields:
            Any: Claude SDK返回的消息

        注意：
        - 该方法是一个异步生成器
        - 取消和错误会被优雅处理，不会向外传播
        - 确保生成器能够正常结束和清理
        """
        logger.info("[SafeClaudeSDK] Starting SDK call")

        try:
            # 调用Claude SDK（内部使用AnyIO TaskGroup）
            # 确保query函数可用（在__init__中已验证SDK_AVAILABLE）
            assert query is not None, "Claude SDK query function is not available"
            # 使用类型忽略来避免BasedPyright的误报
            # query实际需要参数，但BasedPyright可能无法正确推断其签名
            async for message in query(self.prompt, self.options):  # type: ignore[call-arg,misc]
                yield message

        except anyio.get_cancelled_exc_class() as e:
            # 取消异常 - 记录但不重新抛出
            logger.info(f"[SafeClaudeSDK] Cancelled: {e}")
            # 让生成器自然结束

        except Exception as e:
            # 其他异常 - 记录但不重新抛出
            logger.error(f"[SafeClaudeSDK] Error: {e}", exc_info=True)
            # 让生成器自然结束

        finally:
            logger.info("[SafeClaudeSDK] SDK call finished")

    @classmethod
    def is_sdk_available(cls) -> bool:
        """
        检查Claude SDK是否可用

        Returns:
            bool: 如果SDK可用返回True，否则返回False
        """
        return SDK_AVAILABLE

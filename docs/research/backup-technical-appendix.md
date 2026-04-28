# kimi-agent-sdk 迁移技术附录

> 配套文档：`kimi-agent-sdk-removal-comprehensive-report.md`  
> 本文档提供具体的实现细节和代码示例

---

## 目录

1. [适配器实现细节](#1-适配器实现细节)
2. [类型映射表](#2-类型映射表)
3. [异常映射](#3-异常映射)
4. [工具迁移示例](#4-工具迁移示例)
5. [测试迁移指南](#5-测试迁移指南)
6. [回滚策略](#6-回滚策略)

---

## 1. 适配器实现细节

### 1.1 Message 类型适配器

```python
# autoBMAD/docuswarm/adapters/kimi_types.py
"""Kimi SDK 类型适配器 - 提供与 claude-agent-sdk 的兼容层"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast


@dataclass
class ContentPart:
    """Kimi SDK ContentPart 兼容类型"""
    type: str
    text: str | None = None
    name: str | None = None  # for tool_use
    input: dict[str, Any] | None = None  # for tool_use
    
    @classmethod
    def from_claude_block(cls, block: Any) -> "ContentPart":
        """从 Claude SDK block 创建 ContentPart"""
        block_type = type(block).__name__
        
        if block_type == "TextBlock" or hasattr(block, "text"):
            return cls(
                type="text",
                text=getattr(block, "text", str(block))
            )
        elif block_type == "ToolUseBlock" or hasattr(block, "name"):
            return cls(
                type="tool_use",
                name=getattr(block, "name", None),
                input=getattr(block, "input", {}) or {}
            )
        else:
            return cls(type="unknown", text=str(block))


@dataclass
class Message:
    """Kimi SDK Message 兼容类型
    
    提供与 Kimi SDK Message 相同的接口，但底层数据来自 Claude SDK
    """
    role: str
    content: str | list[ContentPart] | None = None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    _raw: Any = field(default=None, repr=False)
    
    def __post_init__(self) -> None:
        """初始化后处理"""
        if self.content is None:
            self.content = ""
    
    @classmethod
    def from_claude_result(
        cls, 
        result: Any, 
        messages: list[Any] | None = None
    ) -> list["Message"]:
        """从 Claude SDK 执行结果创建 Message 列表
        
        Args:
            result: Claude SDK 结果对象
            messages: 中间消息列表
            
        Returns:
            兼容 Kimi SDK 的 Message 列表
        """
        msg_list: list[Message] = []
        
        # 处理中间消息
        if messages:
            for msg in messages:
                if hasattr(msg, "__dict__"):
                    role = getattr(msg, "role", "assistant")
                    content = getattr(msg, "content", None)
                    
                    # 转换 content
                    converted_content: str | list[ContentPart]
                    if isinstance(content, list):
                        converted_content = [
                            ContentPart.from_claude_block(c) 
                            for c in content
                        ]
                    else:
                        converted_content = str(content) if content else ""
                    
                    msg_list.append(cls(
                        role=role,
                        content=converted_content,
                        _raw=msg
                    ))
        
        # 添加最终结果
        if result and hasattr(result, "content"):
            final_content = result.content
            msg_list.append(cls(
                role="assistant",
                content=final_content if final_content else "",
                _raw=result
            ))
        
        return msg_list
    
    def extract_text(self) -> str:
        """提取文本内容 (兼容 Kimi SDK Message 接口)"""
        if self.content is None:
            return ""
        
        if isinstance(self.content, str):
            return self.content
        
        # content 是 list[ContentPart]
        text_parts: list[str] = []
        for part in self.content:
            if isinstance(part, ContentPart) and part.text:
                text_parts.append(part.text)
            elif isinstance(part, dict) and part.get("text"):
                text_parts.append(str(part["text"]))
        
        return "".join(text_parts)


# 类型别名保持兼容
WireMessage = Message
```

### 1.2 MessageAggregator 适配器

```python
# autoBMAD/docuswarm/adapters/message_aggregator.py
"""MessageAggregator 适配器"""

from typing import Any

from autoBMAD.docuswarm.adapters.kimi_types import ContentPart, Message


class MessageAggregator:
    """兼容 Kimi SDK 的 MessageAggregator
    
    由于 Claude SDK 使用不同的流式机制，这个适配器提供接口兼容
    但实际实现有所不同
    """
    
    def __init__(self) -> None:
        """初始化聚合器"""
        self._messages: list[Message] = []
        self._buffered_content: list[str] = []
    
    def feed(self, wire_msg: Any) -> list[Message]:
        """处理流式消息
        
        在 Claude SDK 中，这个消息已经被完整处理，
        所以我们直接转换为 Message 格式
        """
        messages: list[Message] = []
        
        # 尝试提取消息内容
        if hasattr(wire_msg, "role"):
            role = wire_msg.role
            content = getattr(wire_msg, "content", None)
            
            # 转换 content
            if isinstance(content, list):
                converted = [
                    ContentPart.from_claude_block(c) 
                    for c in content
                ]
            else:
                converted = str(content) if content else ""
            
            msg = Message(role=role, content=converted, _raw=wire_msg)
            messages.append(msg)
            self._messages.append(msg)
        
        return messages
    
    def flush(self) -> list[Message]:
        """刷新剩余消息
        
        在当前适配器实现中，消息已经在 feed 中处理，
        所以 flush 返回空列表
        """
        return []
```

### 1.3 异常适配器

```python
# autoBMAD/docuswarm/adapters/exceptions.py
"""Kimi SDK 异常适配器"""


class RunCancelled(Exception):
    """Kimi SDK RunCancelled 兼容异常
    
    在 Claude SDK 中，这对应于 asyncio.CancelledError
    或特定的取消信号
    """
    
    def __init__(self, message: str = "Run was cancelled") -> None:
        self.message = message
        super().__init__(self.message)


class MaxStepsReached(Exception):
    """Kimi SDK MaxStepsReached 兼容异常
    
    在 Claude SDK 中，这可能需要手动检测步骤数
    """
    
    def __init__(self, max_steps: int | None = None) -> None:
        self.max_steps = max_steps
        message = f"Maximum steps ({max_steps}) reached" if max_steps else "Maximum steps reached"
        super().__init__(message)


class ChatProviderError(Exception):
    """Kimi SDK ChatProviderError 兼容异常"""
    
    def __init__(self, message: str, *, error_type: str | None = None) -> None:
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


class ConfigError(Exception):
    """Kimi SDK ConfigError 兼容异常"""
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class InvalidToolError(Exception):
    """Kimi SDK InvalidToolError 兼容异常"""
    
    def __init__(self, message: str, tool_name: str | None = None) -> None:
        self.message = message
        self.tool_name = tool_name
        super().__init__(self.message)


def map_claude_exception(exc: Exception) -> Exception:
    """将 Claude SDK 异常映射到 Kimi SDK 兼容异常
    
    Args:
        exc: 原始异常
        
    Returns:
        映射后的异常
    """
    import asyncio
    
    if isinstance(exc, asyncio.CancelledError):
        return RunCancelled(str(exc))
    
    # 根据异常消息或类型进行映射
    exc_str = str(exc).lower()
    
    if "step" in exc_str and ("max" in exc_str or "limit" in exc_str):
        return MaxStepsReached()
    
    if "tool" in exc_str and ("invalid" in exc_str or "unknown" in exc_str):
        return InvalidToolError(str(exc))
    
    if "config" in exc_str or "configuration" in exc_str:
        return ConfigError(str(exc))
    
    if "provider" in exc_str or "api" in exc_str:
        return ChatProviderError(str(exc))
    
    # 无法映射，返回原异常
    return exc
```

### 1.4 KaosPath 适配器

```python
# autoBMAD/docuswarm/adapters/kaos_path.py
"""KaosPath 适配器 - 提供 Path 兼容性"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class KaosPath:
    """兼容 kimi-agent-sdk 的 KaosPath
    
    实际上是对 pathlib.Path 的包装
    """
    
    def __init__(self, path: str | Path | "KaosPath") -> None:
        """初始化 KaosPath
        
        Args:
            path: 路径字符串、Path 对象或另一个 KaosPath
        """
        if isinstance(path, KaosPath):
            self._path = path._path
        elif isinstance(path, Path):
            self._path = path
        else:
            self._path = Path(str(path))
    
    @classmethod
    def cwd(cls) -> "KaosPath":
        """获取当前工作目录"""
        return cls(Path.cwd())
    
    def __str__(self) -> str:
        return str(self._path)
    
    def __repr__(self) -> str:
        return f"KaosPath({repr(str(self._path))})"
    
    def __truediv__(self, other: str | Path) -> "KaosPath":
        """支持 / 操作符"""
        return KaosPath(self._path / other)
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, KaosPath):
            return self._path == other._path
        elif isinstance(other, Path):
            return self._path == other
        return False
    
    def __hash__(self) -> int:
        return hash(self._path)
    
    @property
    def path(self) -> Path:
        """获取底层 Path 对象"""
        return self._path
    
    def resolve(self) -> "KaosPath":
        """解析绝对路径"""
        return KaosPath(self._path.resolve())
    
    def exists(self) -> bool:
        """检查路径是否存在"""
        return self._path.exists()
    
    def mkdir(self, parents: bool = False, exist_ok: bool = False) -> None:
        """创建目录"""
        self._path.mkdir(parents=parents, exist_ok=exist_ok)
    
    def is_file(self) -> bool:
        """检查是否为文件"""
        return self._path.is_file()
    
    def is_dir(self) -> bool:
        """检查是否为目录"""
        return self._path.is_dir()
    
    def read_text(self, encoding: str = "utf-8") -> str:
        """读取文本文件"""
        return self._path.read_text(encoding=encoding)
    
    def write_text(self, content: str, encoding: str = "utf-8") -> None:
        """写入文本文件"""
        self._path.write_text(content, encoding=encoding)
```

---

## 2. 类型映射表

### 2.1 完整类型映射

| Kimi SDK 类型 | Claude SDK 对应 | 适配器实现 | 备注 |
|--------------|----------------|-----------|------|
| `Session` | `query()` 函数 | 包装为 Session 类 | 语义不同 |
| `Message` | `ResultMessage` | `Message.from_claude_result()` | 需要转换 |
| `WireMessage` | `ResultMessage` | 别名到 Message | 类似 |
| `MessageAggregator` | 无需 | 简化实现 | Claude 不需要 |
| `Config` | 环境变量 | 兼容层 | 配置方式不同 |
| `KaosPath` | `Path` | 包装类 | 简化实现 |
| `ApprovalRequest` | 无 | 模拟类 | 需特殊处理 |
| `CallableTool2` | 函数 | 装饰器包装 | 范式转换 |
| `ToolOk` | 无 | dataclass | 结果包装 |
| `ToolError` | Exception | dataclass | 错误包装 |
| `RunCancelled` | `CancelledError` | 异常类 | 需捕获转换 |
| `MaxStepsReached` | 无 | 手动检测 | 需额外逻辑 |
| `ChatProviderError` | 各种 API 异常 | 异常类 | 需映射 |
| `ConfigError` | `ValueError` | 异常类 | 配置错误 |

### 2.2 方法映射表

| Kimi SDK 方法 | Claude SDK 对应 | 适配器方法 |
|--------------|----------------|-----------|
| `Session.create()` | `query()` | `UnifiedSessionManager.create_session()` |
| `session.prompt()` | `query()` 返回的 generator | 包装为 async generator |
| `session.close()` | 无需 | 空操作或清理 |
| `MessageAggregator.feed()` | 无需 | 直接转换消息 |
| `MessageAggregator.flush()` | 无需 | 返回空列表 |

---

## 3. 异常映射

### 3.1 异常处理适配器

```python
# autoBMAD/docuswarm/adapters/exception_handler.py
"""异常处理适配器 - 统一异常处理"""

import functools
import logging
from typing import Any, Callable, TypeVar

from autoBMAD.docuswarm.adapters.exceptions import (
    ChatProviderError,
    ConfigError,
    InvalidToolError,
    MaxStepsReached,
    RunCancelled,
)

F = TypeVar("F", bound=Callable[..., Any])

logger = logging.getLogger(__name__)


def adapt_exceptions(func: F) -> F:
    """装饰器：自动将 Claude SDK 异常映射到 Kimi SDK 异常
    
    用法:
        @adapt_exceptions
        async def my_function():
            ...
    """
    
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        import asyncio
        
        try:
            return await func(*args, **kwargs)
        
        except asyncio.CancelledError:
            # 直接重抛为 RunCancelled
            raise RunCancelled("Operation was cancelled")
        
        except Exception as e:
            # 映射异常
            mapped = map_exception(e)
            if mapped is not e:
                raise mapped from e
            raise
    
    return wrapper  # type: ignore[return-value]


def map_exception(exc: Exception) -> Exception:
    """将异常映射到 Kimi SDK 兼容异常
    
    Args:
        exc: 原始异常
        
    Returns:
        映射后的异常（如果无法映射则返回原异常）
    """
    import asyncio
    
    # 已经是目标异常类型
    if isinstance(exc, (RunCancelled, MaxStepsReached, ChatProviderError, 
                       ConfigError, InvalidToolError)):
        return exc
    
    # asyncio.CancelledError -> RunCancelled
    if isinstance(exc, asyncio.CancelledError):
        return RunCancelled(str(exc))
    
    # 基于异常类型映射
    exc_type = type(exc).__name__
    exc_str = str(exc).lower()
    
    # API 相关错误
    if exc_type in ("APIError", "APITimeoutError", "APIConnectionError"):
        return ChatProviderError(str(exc), error_type=exc_type)
    
    # 配置相关错误
    if exc_type in ("ValidationError", "ConfigValidationError"):
        return ConfigError(str(exc))
    
    # 基于消息内容映射
    if "step" in exc_str and ("max" in exc_str or "limit" in exc_str):
        return MaxStepsReached()
    
    if "tool" in exc_str and ("invalid" in exc_str or "unknown" in exc_str):
        tool_name = _extract_tool_name(exc_str)
        return InvalidToolError(str(exc), tool_name=tool_name)
    
    if "cancel" in exc_str or "abort" in exc_str:
        return RunCancelled(str(exc))
    
    # 无法映射，返回原异常
    return exc


def _extract_tool_name(exc_str: str) -> str | None:
    """从异常消息中提取工具名称"""
    import re
    
    # 尝试匹配常见的工具名称模式
    patterns = [
        r'tool[\s\']*["\']?(\w+)["\']?',
        r'["\']?(\w+)["\']?[\s\']*tool',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, exc_str)
        if match:
            return match.group(1)
    
    return None
```

---

## 4. 工具迁移示例

### 4.1 CallableTool2 兼容层

```python
# autoBMAD/docuswarm/adapters/tools.py
"""工具适配器 - 提供 CallableTool2 兼容层"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Coroutine, TypeVar, get_type_hints

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    output: str
    error: str | None = None
    
    def to_kimi_ok(self) -> "ToolOk":
        """转换为 Kimi SDK ToolOk"""
        return ToolOk(output=self.output)
    
    def to_kimi_error(self) -> "ToolError":
        """转换为 Kimi SDK ToolError"""
        return ToolError(
            output=self.output,
            message=self.error or "Unknown error",
            brief=self.error[:100] if self.error else "Error"
        )


@dataclass
class ToolOk:
    """Kimi SDK ToolOk 兼容"""
    output: str


@dataclass  
class ToolError:
    """Kimi SDK ToolError 兼容"""
    output: str
    message: str
    brief: str


ToolReturnValue = ToolOk | ToolError


def tool_adapter(
    name: str | None = None,
    description: str | None = None
) -> Callable[[Callable[..., Coroutine[Any, Any, ToolResult]]], "CallableTool2Adapter"]:
    """工具适配器装饰器
    
    将异步函数转换为 CallableTool2 兼容的工具
    
    用法:
        @tool_adapter(name="create_deliverable")
        async def create_deliverable(params: dict[str, Any]) -> ToolResult:
            ...
    """
    
    def decorator(
        func: Callable[..., Coroutine[Any, Any, ToolResult]]
    ) -> "CallableTool2Adapter":
        return CallableTool2Adapter(
            func=func,
            name=name or func.__name__,
            description=description or func.__doc__ or "",
        )
    
    return decorator


class CallableTool2Adapter:
    """CallableTool2 兼容适配器
    
    包装异步函数，提供 CallableTool2 接口
    """
    
    def __init__(
        self,
        func: Callable[..., Coroutine[Any, Any, ToolResult]],
        name: str,
        description: str,
    ) -> None:
        self.func = func
        self.name = name
        self.description = description
        self._params_type = self._extract_params_type()
    
    def _extract_params_type(self) -> type[BaseModel] | None:
        """提取参数类型"""
        hints = get_type_hints(self.func)
        # 假设第一个参数是 params
        param_types = [t for n, t in hints.items() if n != "return"]
        if param_types:
            param_type = param_types[0]
            if isinstance(param_type, type) and issubclass(param_type, BaseModel):
                return param_type
        return None
    
    async def __call__(self, params: Any) -> ToolReturnValue:
        """执行工具
        
        Args:
            params: 工具参数（可以是 dict 或 Pydantic model）
            
        Returns:
            ToolOk 或 ToolError
        """
        try:
            # 转换参数
            if isinstance(params, dict) and self._params_type:
                params = self._params_type(**params)
            
            # 执行函数
            result = await self.func(params if not isinstance(params, dict) else params)
            
            # 返回 Kimi 格式结果
            if result.success:
                return result.to_kimi_ok()
            else:
                return result.to_kimi_error()
                
        except Exception as e:
            return ToolError(
                output="",
                message=str(e),
                brief=f"Execution failed: {e}"
            )
```

### 4.2 具体工具迁移示例

```python
# autoBMAD/docuswarm/tools/create_deliverable_migrated.py
"""CreateDeliverableTool - 迁移后版本"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import aiofiles
from pydantic import BaseModel, Field

from autoBMAD.docuswarm.adapters.tools import (
    ToolResult,
    ToolReturnValue,
    tool_adapter,
)

# 保留 Kimi SDK 兼容导入
from kimi_agent_sdk import CallableTool2, ToolOk, ToolError  # type: ignore[import]


class CreateDeliverableParams(BaseModel):
    """参数模型"""
    title: str = Field(description="Deliverable title")
    content: str = Field(description="Deliverable content (Markdown)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata")


def _slugify_filename(title: str) -> str:
    """转换标题为文件名"""
    slug = title.lower()
    slug = slug.replace(" ", "-")
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return f"{slug}.md"


# ============ 新实现：函数式 + 适配器装饰器 ============

@tool_adapter(name="create_deliverable")
async def create_deliverable_func(params: CreateDeliverableParams) -> ToolResult:
    """函数式实现 - 不依赖 CallableTool2"""
    try:
        filename = _slugify_filename(params.title)
        file_path = Path.cwd() / filename
        
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(params.content)
        
        return ToolResult(
            success=True,
            output=f"Deliverable '{params.title}' saved to {file_path}"
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            output="",
            error=str(exc)
        )


# ============ 兼容层：保持 CallableTool2 接口 ============

class CreateDeliverableTool(CallableTool2[CreateDeliverableParams]):  # type: ignore[misc]
    """Kimi SDK CallableTool2 兼容类
    
    内部使用新函数式实现
    """
    
    name: str = "create_deliverable"
    description: str = "Create a node deliverable document"
    params: type[CreateDeliverableParams] = CreateDeliverableParams
    
    def __init__(self) -> None:
        super().__init__()
        self._adapter = create_deliverable_func
    
    async def __call__(self, params: CreateDeliverableParams) -> ToolReturnValue:
        """委托给适配器"""
        result = await self._adapter(params)
        
        # 转换为 Kimi SDK 格式
        if result.success:
            return ToolOk(output=result.output)
        else:
            return ToolError(
                output=result.output,
                message=result.error or "Failed",
                brief=result.error[:100] if result.error else "Failed"
            )
```

---

## 5. 测试迁移指南

### 5.1 Mock 策略更新

```python
# tests/conftest.py (迁移后)
"""Pytest 全局配置 - 迁移后版本"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture(autouse=True)
def mock_sdk():
    """全局 mock SDK - 统一接口"""
    # 创建统一的 mock 结果
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.content = "Mock response"
    mock_result.error = None
    mock_result.messages = []
    mock_result.duration = 0.1
    
    # Mock Claude SDK
    with patch("autoBMAD.docuswarm.llm.claude_sdk_wrapper._query") as mock_query:
        async def async_gen():
            yield mock_result
        
        mock_query.return_value = async_gen()
        yield mock_query


@pytest.fixture
def mock_session_manager():
    """Mock UnifiedSessionManager"""
    manager = AsyncMock()
    
    # Mock single_prompt 返回 Message 格式
    async def mock_single_prompt(prompt, **kwargs):
        from autoBMAD.docuswarm.adapters.kimi_types import Message
        return [Message(role="assistant", content="Mock response")]
    
    manager.single_prompt = mock_single_prompt
    manager.create_session = AsyncMock()
    manager.close = AsyncMock()
    
    return manager
```

### 5.2 测试用例迁移示例

```python
# tests/unit/test_independent_agent_migrated.py
"""IndependentAgent 测试 - 迁移后"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from autoBMAD.docuswarm.agents.independent import IndependentAgent


@pytest.mark.asyncio
async def test_independent_agent_execution_migrated(mock_session_manager):
    """测试 IndependentAgent 执行 - 使用新 mock"""
    
    # 配置 mock 返回 Message 格式
    from autoBMAD.docuswarm.adapters.kimi_types import Message, ContentPart
    
    mock_session_manager.single_prompt.return_value = [
        Message(
            role="assistant",
            content=[
                ContentPart(
                    type="tool_use",
                    name="create_deliverable",
                    input={
                        "title": "Test Deliverable",
                        "content": "Test content"
                    }
                )
            ]
        ),
        Message(
            role="assistant",
            content='{"deliverable": {"title": "Test", "content": "Test"}, "questions": []}'
        )
    ]
    
    # 创建 agent 并执行
    config = MagicMock()
    agent = IndependentAgent(
        config=config,
        session_manager=mock_session_manager,
        node_id="test"
    )
    
    context = {
        "task": "Create test deliverable",
        "pipeline_id": "test-123",
        "subject_context": {"subject": "test"}
    }
    
    result = await agent.execute(context)
    
    # 验证结果
    assert "deliverable" in result
    mock_session_manager.single_prompt.assert_called_once()
```

---

## 6. 回滚策略

### 6.1 版本控制策略

```bash
# 建议的 Git 分支策略
git checkout -b feature/remove-kimi-sdk-phase-1
# Phase 1 完成后
git checkout -b feature/remove-kimi-sdk-phase-2
# 依此类推...

# 每个 Phase 独立 PR，便于回滚
```

### 6.2 功能开关

```python
# autoBMAD/docuswarm/config.py

class SDKConfig:
    """SDK 配置 - 支持功能开关"""
    
    USE_CLAUDE_SDK_ONLY: bool = False  # 功能开关
    
    @classmethod
    def get_session_manager_class(cls):
        """根据配置返回 SessionManager 类"""
        if cls.USE_CLAUDE_SDK_ONLY:
            from autoBMAD.docuswarm.llm.unified_session_manager import UnifiedSessionManager
            return UnifiedSessionManager
        else:
            from autoBMAD.docuswarm.llm.session_manager import KimiSessionManager
            return KimiSessionManager
```

### 6.3 回滚检查清单

- [ ] 所有 Phase 都有独立分支
- [ ] 每个 PR 都有完整的测试通过
- [ ] 保留原始 Kimi SDK 代码的备份分支
- [ ] 生产环境可以切换功能开关
- [ ] 监控和告警已配置

---

## 附录 A：迁移检查清单

### Phase 1: 适配器层
- [ ] `adapters/kimi_types.py` 实现
- [ ] `adapters/message_aggregator.py` 实现
- [ ] `adapters/exceptions.py` 实现
- [ ] `adapters/kaos_path.py` 实现
- [ ] 单元测试通过

### Phase 2: SessionManager
- [ ] UnifiedSessionManager 实现
- [ ] KimiSessionManager 重构为适配器
- [ ] 所有类型注解更新
- [ ] 集成测试通过

### Phase 3: Agent 层
- [ ] IndependentAgent 导入更新
- [ ] EvaluatorAgent 导入更新
- [ ] 异常处理更新
- [ ] Agent 测试通过

### Phase 4: Tools 层
- [ ] 6 个工具文件迁移
- [ ] 兼容层测试通过
- [ ] 工具集成测试通过

### Phase 5: 依赖清理
- [ ] `pyproject.toml` 更新
- [ ] `requirements.txt` 更新
- [ ] 文档更新

### Phase 6: 测试
- [ ] conftest.py 重写
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 端到端测试通过

---

*本文档为 `kimi-agent-sdk-removal-comprehensive-report.md` 的技术附录*  
*更新日期: 2026-03-02*

# Claude Agent SDK 调用架构设计文档

> **用途**: 为其他项目提供 Claude Agent SDK 调用开发参考
> **版本**: 1.0
> **基于**: epic_automation 工作流实现

---

## 目录

1. [架构概述](#1-架构概述)
2. [核心组件](#2-核心组件)
3. [数据结构](#3-数据结构)
4. [调用流程](#4-调用流程)
5. [取消机制](#5-取消机制)
6. [错误处理](#6-错误处理)
7. [快速接入指南](#7-快速接入指南)
8. [最佳实践](#8-最佳实践)

---

## 1. 架构概述

### 1.1 五层架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     业务层 (Agent Layer)                      │
│  SMAgent, DevAgent, QAAgent, StatusUpdateAgent, etc.         │
├─────────────────────────────────────────────────────────────┤
│                    辅助层 (Helper Layer)                      │
│                      sdk_helper.py                           │
│           execute_sdk_call(), get_sdk_options()              │
├─────────────────────────────────────────────────────────────┤
│                    执行层 (Executor Layer)                    │
│                      SDKExecutor                             │
│           TaskGroup隔离, 流式消息收集, 目标检测               │
├─────────────────────────────────────────────────────────────┤
│                    包装层 (Wrapper Layer)                     │
│  SafeClaudeSDK, SafeAsyncGenerator, SDKMessageTracker        │
│           异步生成器管理, 消息提取, 取消恢复                  │
├─────────────────────────────────────────────────────────────┤
│                     核心层 (Core Layer)                       │
│         CancellationManager, SDKResult, SDKErrorType         │
│            双条件验证, 结果封装, 错误类型枚举                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 设计原则

1. **任务隔离**: SDK调用在独立TaskGroup中执行，防止Cancel Scope跨任务传播
2. **双条件验证**: 取消成功需同时满足 `cancel_requested` 和 `cleanup_completed`
3. **奥卡姆剃刀**: 移除分散的取消逻辑，统一由CancellationManager管理
4. **优雅降级**: SDK不可用时返回明确错误，不阻塞业务流程

---

## 2. 核心组件

### 2.1 CancellationManager (取消管理器)

**职责**: 管理SDK调用生命周期、取消请求和资源清理

```python
from dataclasses import dataclass, field
from typing import AsyncIterator
from contextlib import asynccontextmanager
import anyio
import logging
import time

@dataclass
class CallInfo:
    """SDK调用信息"""
    call_id: str
    agent_name: str
    start_time: float
    cancel_requested: bool = False
    cleanup_completed: bool = False
    has_target_result: bool = False
    errors: list[str] = field(default_factory=list)


class CancellationManager:
    """取消管理器 - 双条件验证机制"""
    
    def __init__(self) -> None:
        self._active_calls: dict[str, CallInfo] = {}
        self._lock = anyio.Lock()
    
    def register_call(self, call_id: str, agent_name: str) -> None:
        """注册SDK调用"""
        self._active_calls[call_id] = CallInfo(
            call_id=call_id,
            agent_name=agent_name,
            start_time=time.time()
        )
    
    def request_cancel(self, call_id: str) -> None:
        """请求取消"""
        if call_id in self._active_calls:
            self._active_calls[call_id].cancel_requested = True
    
    def mark_cleanup_completed(self, call_id: str) -> None:
        """标记清理完成"""
        if call_id in self._active_calls:
            self._active_calls[call_id].cleanup_completed = True
    
    def mark_target_result_found(self, call_id: str) -> None:
        """标记找到目标结果"""
        if call_id in self._active_calls:
            self._active_calls[call_id].has_target_result = True
    
    @asynccontextmanager
    async def track_sdk_execution(
        self, call_id: str, agent_name: str, operation_name: str | None = None
    ) -> AsyncIterator[None]:
        """跟踪SDK执行的异步上下文管理器"""
        self.register_call(call_id, agent_name)
        try:
            yield
        finally:
            self.mark_cleanup_completed(call_id)
    
    async def confirm_safe_to_proceed(self, call_id: str, timeout: float = 30.0) -> bool:
        """确认可以安全继续 - 双条件验证"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if call_id in self._active_calls:
                call_info = self._active_calls[call_id]
                if call_info.cancel_requested and call_info.cleanup_completed:
                    return True
            await anyio.sleep(0.1)
        return False
    
    def unregister_call(self, call_id: str) -> None:
        """注销调用"""
        self._active_calls.pop(call_id, None)
    
    def get_call_info(self, call_id: str) -> CallInfo | None:
        """获取调用信息"""
        return self._active_calls.get(call_id)
```

### 2.2 SDKResult (结果封装)

**职责**: 标准化SDK执行结果，提供业务判断方法

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SDKErrorType(Enum):
    """SDK错误类型枚举"""
    SUCCESS = "success"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    SDK_ERROR = "sdk_error"
    CANCEL_SCOPE_ERROR = "cancel_scope_error"
    UNKNOWN = "unknown"


@dataclass
class SDKResult:
    """SDK执行结果数据类"""
    
    # 业务成功标志（Agent只关注这两个字段）
    has_target_result: bool = False
    cleanup_completed: bool = False
    
    # 执行信息
    duration_seconds: float = 0.0
    session_id: str = ""
    agent_name: str = ""
    
    # 结果数据
    messages: list[Any] = field(default_factory=list)
    target_message: Any = None
    
    # 错误信息
    error_type: SDKErrorType = SDKErrorType.SUCCESS
    errors: list[str] = field(default_factory=list)
    last_exception: BaseException | None = None
    
    def is_success(self) -> bool:
        """业务是否成功 = 获得目标结果 AND 完成清理"""
        return self.has_target_result and self.cleanup_completed
    
    def is_cancelled(self) -> bool:
        return self.error_type == SDKErrorType.CANCELLED
    
    def is_timeout(self) -> bool:
        return self.error_type == SDKErrorType.TIMEOUT
    
    def has_cancel_scope_error(self) -> bool:
        return self.error_type == SDKErrorType.CANCEL_SCOPE_ERROR
    
    def get_error_summary(self) -> str:
        if self.is_success():
            return "Success"
        return f"{self.error_type.value} ({len(self.errors)} errors)"
```

### 2.3 SDKExecutor (执行器)

**职责**: 在独立TaskGroup中执行SDK调用，确保Cancel Scope隔离

```python
import anyio
import time
import uuid
from typing import Callable, Any, Union, Awaitable
from collections.abc import AsyncIterator


class SDKExecutor:
    """SDK执行器 - TaskGroup隔离执行"""
    
    def __init__(self) -> None:
        self.cancel_manager = CancellationManager()
    
    async def execute(
        self,
        sdk_func: Union[Callable[[], AsyncIterator[Any]], Callable[[], Awaitable[Any]]],
        target_predicate: Callable[[Any], bool],
        *,
        timeout: float | None = None,
        agent_name: str = "Unknown"
    ) -> SDKResult:
        """
        在独立TaskGroup中执行SDK调用
        
        Args:
            sdk_func: SDK调用函数（异步生成器或协程）
            target_predicate: 目标消息检测函数
            timeout: 超时时间
            agent_name: Agent名称
        
        Returns:
            SDKResult: 标准化执行结果
        """
        call_id = str(uuid.uuid4())
        session_id = f"{agent_name}-{call_id[:8]}"
        start_time = time.time()
        
        try:
            async with anyio.create_task_group() as sdk_tg:
                result = await self._execute_in_taskgroup(
                    sdk_tg, sdk_func, target_predicate,
                    call_id, agent_name, timeout
                )
                return result
        except Exception as e:
            return SDKResult(
                has_target_result=False,
                cleanup_completed=False,
                duration_seconds=time.time() - start_time,
                session_id=session_id,
                agent_name=agent_name,
                error_type=SDKErrorType.UNKNOWN,
                errors=[str(e)],
                last_exception=e
            )
    
    async def _execute_in_taskgroup(
        self, task_group, sdk_func, target_predicate,
        call_id: str, agent_name: str, timeout: float | None
    ) -> SDKResult:
        """TaskGroup内执行逻辑"""
        self.cancel_manager.register_call(call_id, agent_name)
        messages = []
        target_message = None
        errors = []
        start_time = time.time()
        
        try:
            # 处理异步生成器
            sdk_generator = sdk_func()
            async for message in sdk_generator:
                messages.append(message)
                
                # 目标检测
                if target_predicate(message):
                    target_message = message
                    self.cancel_manager.mark_target_result_found(call_id)
                    self.cancel_manager.request_cancel(call_id)
            
            # 标记清理完成
            self.cancel_manager.mark_cleanup_completed(call_id)
            
            # 等待确认
            safe = await self.cancel_manager.confirm_safe_to_proceed(call_id)
            
            return SDKResult(
                has_target_result=target_message is not None,
                cleanup_completed=safe,
                duration_seconds=time.time() - start_time,
                session_id=f"{agent_name}-{call_id[:8]}",
                agent_name=agent_name,
                messages=messages,
                target_message=target_message,
                error_type=SDKErrorType.SUCCESS if target_message else SDKErrorType.UNKNOWN,
                errors=errors if not target_message else []
            )
            
        except anyio.get_cancelled_exc_class():
            return SDKResult(
                has_target_result=False,
                cleanup_completed=False,
                duration_seconds=time.time() - start_time,
                agent_name=agent_name,
                error_type=SDKErrorType.CANCELLED
            )
        finally:
            self.cancel_manager.unregister_call(call_id)
```

### 2.4 SafeClaudeSDK (安全包装器)

**职责**: 封装Claude SDK，处理跨任务取消错误和异步生成器生命周期

```python
class SafeAsyncGenerator:
    """安全的异步生成器包装器"""
    
    def __init__(self, generator: AsyncIterator[Any], cleanup_timeout: float = 1.0):
        self.generator = generator
        self.cleanup_timeout = cleanup_timeout
        self._closed = False
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self._closed:
            raise StopAsyncIteration
        try:
            return await self.generator.__anext__()
        except StopAsyncIteration:
            self._closed = True
            raise
    
    async def aclose(self) -> None:
        """安全清理 - 防止cancel scope跨任务错误"""
        if self._closed:
            return
        self._closed = True
        # 在同一Task中完成清理，不跨Task


class SafeClaudeSDK:
    """Claude SDK安全包装器"""
    
    def __init__(
        self, prompt: str, options: Any,
        timeout: float | None = None, log_manager: Any = None
    ):
        self.prompt = prompt
        self.options = options
        self.timeout = timeout
        self.message_tracker = SDKMessageTracker(log_manager)
    
    async def execute(self) -> bool:
        """执行SDK查询 - 含跨任务错误恢复"""
        max_retries = 2
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                return await self._execute_with_recovery()
            except RuntimeError as e:
                error_msg = str(e)
                if "cancel scope" in error_msg.lower() and "different task" in error_msg.lower():
                    # 检查是否已收到结果
                    manager = get_cancellation_manager()
                    if manager._active_calls:
                        latest = list(manager._active_calls.values())[-1]
                        if latest.has_target_result:
                            return True  # 视为成功
                    
                    retry_count += 1
                    if retry_count > max_retries:
                        raise
                    await self._rebuild_execution_context()
                else:
                    raise
        return False
    
    async def _execute_with_recovery(self) -> bool:
        """核心执行逻辑"""
        manager = get_cancellation_manager()
        call_id = f"sdk_{id(self)}_{int(time.time() * 1000)}"
        
        try:
            async with manager.track_sdk_execution(call_id, "SafeClaudeSDK"):
                return await self._execute_safely_with_manager(manager, call_id)
        except asyncio.CancelledError:
            call_info = manager.get_call_info(call_id)
            if call_info and call_info.has_target_result:
                await manager.confirm_safe_to_proceed(call_id, timeout=5.0)
                return True
            return False
```

### 2.5 sdk_helper (统一调用接口)

**职责**: 为Agent提供简化的SDK调用入口

```python
from pathlib import Path


async def execute_sdk_call(
    prompt: str,
    agent_name: str,
    *,
    timeout: float | None = 1800.0,
    permission_mode: str = "bypassPermissions",
    cwd: str | None = None
) -> SDKResult:
    """
    SDK调用统一入口
    
    Args:
        prompt: 提示词
        agent_name: Agent名称
        timeout: 超时时间（秒）
        permission_mode: 权限模式
        cwd: 工作目录
    
    Returns:
        SDKResult: 执行结果
    
    Example:
        result = await execute_sdk_call(
            prompt="请分析代码...",
            agent_name="DevAgent",
            timeout=600.0
        )
        if result.is_success():
            # 处理成功
            content = result.target_message
    """
    # SDK可用性检查
    if not SDK_AVAILABLE:
        return SDKResult(
            has_target_result=False,
            cleanup_completed=True,
            error_type=SDKErrorType.SDK_ERROR,
            errors=["Claude Agent SDK not installed"]
        )
    
    # 创建SDK选项
    from claude_agent_sdk import ClaudeAgentOptions
    options = ClaudeAgentOptions(
        permission_mode=permission_mode,
        cwd=cwd or str(Path.cwd())
    )
    
    # 创建执行器
    executor = SDKExecutor()
    
    # 定义SDK函数
    async def sdk_func():
        gen = query(prompt=prompt, options=options)
        async for message in gen:
            yield message
    
    # 定义目标检测
    def target_predicate(message) -> bool:
        return isinstance(message, ResultMessage) and not message.is_error
    
    # 执行
    return await executor.execute(
        sdk_func=sdk_func,
        target_predicate=target_predicate,
        timeout=timeout,
        agent_name=agent_name
    )


def get_sdk_options(**overrides) -> dict[str, Any]:
    """获取统一SDK配置"""
    return {
        'permission_mode': 'bypassPermissions',
        'cwd': str(Path.cwd()),
        **overrides
    }
```

---

## 3. 数据结构

### 3.1 消息类型

Claude Agent SDK返回的消息类型：

| 类型 | 说明 | 关键属性 |
|------|------|----------|
| `SystemMessage` | 系统消息 | `subtype`: init/tool |
| `AssistantMessage` | 助手响应 | `content`: TextBlock/ThinkingBlock/ToolUseBlock |
| `UserMessage` | 用户输入 | `content`: str/list |
| `ResultMessage` | 最终结果 | `is_error`, `result`, `num_turns` |

### 3.2 错误类型枚举

```python
class SDKErrorType(Enum):
    SUCCESS = "success"            # 执行成功
    CANCELLED = "cancelled"        # 被取消
    TIMEOUT = "timeout"            # 超时
    SDK_ERROR = "sdk_error"        # SDK内部错误
    CANCEL_SCOPE_ERROR = "cancel_scope_error"  # Cancel Scope错误
    UNKNOWN = "unknown"            # 未知错误
```

---

## 4. 调用流程

### 4.1 标准调用流程

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│   Agent     │────▶│  sdk_helper  │────▶│  SDKExecutor   │
│             │     │              │     │                │
│ execute_sdk │     │ execute_sdk  │     │  execute()     │
│ _call()     │     │ _call()      │     │                │
└─────────────┘     └──────────────┘     └────────┬───────┘
                                                  │
                    ┌─────────────────────────────┘
                    ▼
┌───────────────────────────────────────────────────────────┐
│                   独立 TaskGroup                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 1. register_call(call_id, agent_name)               │  │
│  │ 2. sdk_generator = sdk_func()                       │  │
│  │ 3. async for message in sdk_generator:              │  │
│  │       if target_predicate(message):                 │  │
│  │           mark_target_result_found()                │  │
│  │           request_cancel()                          │  │
│  │ 4. mark_cleanup_completed()                         │  │
│  │ 5. confirm_safe_to_proceed()                        │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
                    │
                    ▼
            ┌───────────────┐
            │   SDKResult   │
            │   is_success  │
            └───────────────┘
```

### 4.2 时序图

```
Agent          sdk_helper       SDKExecutor    CancelManager    Claude SDK
  │                │                │               │               │
  │ execute_sdk()  │                │               │               │
  │───────────────▶│                │               │               │
  │                │  execute()     │               │               │
  │                │───────────────▶│               │               │
  │                │                │ register_call │               │
  │                │                │──────────────▶│               │
  │                │                │               │               │
  │                │                │  query()                      │
  │                │                │──────────────────────────────▶│
  │                │                │               │               │
  │                │                │    message stream             │
  │                │                │◀─────────────────────────────◀│
  │                │                │               │               │
  │                │                │ mark_target_  │               │
  │                │                │ result_found  │               │
  │                │                │──────────────▶│               │
  │                │                │               │               │
  │                │                │ request_cancel│               │
  │                │                │──────────────▶│               │
  │                │                │               │               │
  │                │                │ mark_cleanup_ │               │
  │                │                │ completed     │               │
  │                │                │──────────────▶│               │
  │                │                │               │               │
  │                │                │confirm_safe   │               │
  │                │                │──────────────▶│               │
  │                │                │◀──────────────│ (true/false)  │
  │                │   SDKResult    │               │               │
  │◀───────────────│◀───────────────│               │               │
```

---

## 5. 取消机制

### 5.1 双条件验证机制

取消被认为安全完成需要同时满足：

1. **cancel_requested = True**: 已请求取消
2. **cleanup_completed = True**: 资源已清理

```python
async def confirm_safe_to_proceed(call_id: str, timeout: float = 30.0) -> bool:
    """双条件验证"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        call_info = self._active_calls.get(call_id)
        if call_info:
            # 双条件同时满足才返回True
            if call_info.cancel_requested and call_info.cleanup_completed:
                return True
        await anyio.sleep(0.1)
    return False
```

### 5.2 跨任务取消错误处理

当检测到 "cancel scope in different task" 错误时：

```python
if "cancel scope" in error_msg.lower() and "different task" in error_msg.lower():
    # 1. 检查是否已收到结果
    if manager._active_calls and latest_call.has_target_result:
        return True  # 视为成功
    
    # 2. 重建执行上下文
    await self._rebuild_execution_context()
    
    # 3. 重试（最多2次）
    retry_count += 1
```

### 5.3 CancelledError处理

```python
except asyncio.CancelledError:
    call_info = manager.get_call_info(call_id)
    cancel_type = "after_success" if (call_info and call_info.has_target_result) else "immediate"
    
    if cancel_type == "after_success":
        # 工作已完成，等待清理
        await manager.confirm_safe_to_proceed(call_id, timeout=5.0)
        return True
    else:
        # 真正取消，返回False但不中断工作流
        return False
```

---

## 6. 错误处理

### 6.1 错误分类处理

| 错误类型 | 处理策略 |
|----------|----------|
| SDK不可用 | 返回SDK_ERROR，cleanup_completed=True |
| 取消 | 检查是否已获得结果，决定返回值 |
| 超时 | 返回TIMEOUT类型 |
| Cancel Scope错误 | 检查结果/重建上下文/重试 |
| 其他异常 | 封装到SDKResult，不抛出 |

### 6.2 降级策略

```python
# SDK不可用时的降级处理
if not SDK_AVAILABLE:
    return SDKResult(
        has_target_result=False,
        cleanup_completed=True,  # 标记清理完成避免阻塞
        error_type=SDKErrorType.SDK_ERROR,
        errors=["Claude Agent SDK not installed"]
    )
```

---

## 7. 快速接入指南

### 7.1 最小实现

```python
from your_sdk_core import execute_sdk_call, SDKResult

async def your_agent_method(self, prompt: str) -> bool:
    """Agent中调用SDK的最简方式"""
    result = await execute_sdk_call(
        prompt=prompt,
        agent_name="YourAgent",
        timeout=600.0
    )
    return result.is_success()
```

### 7.2 完整实现示例

```python
from your_sdk_core import execute_sdk_call, SDKResult, SDKErrorType

class YourAgent:
    async def process_task(self, task_content: str) -> dict:
        # 构建提示词
        prompt = f"""请处理以下任务：
{task_content}

要求：
1. 完成任务后返回结果
2. 如有问题请说明
"""
        
        # 调用SDK
        result = await execute_sdk_call(
            prompt=prompt,
            agent_name="YourAgent",
            timeout=1800.0,
            permission_mode="bypassPermissions"
        )
        
        # 处理结果
        if result.is_success():
            return {
                "status": "success",
                "duration": result.duration_seconds,
                "message_count": len(result.messages)
            }
        elif result.is_cancelled():
            return {
                "status": "cancelled",
                "errors": result.errors
            }
        elif result.is_timeout():
            return {
                "status": "timeout",
                "duration": result.duration_seconds
            }
        else:
            return {
                "status": "failed",
                "error_type": result.error_type.value,
                "errors": result.errors
            }
```

### 7.3 项目集成步骤

1. **复制核心模块**:
   - `sdk_result.py` - 结果封装
   - `cancellation_manager.py` - 取消管理器
   - `sdk_executor.py` - 执行器
   - `sdk_helper.py` - 辅助函数

2. **配置全局管理器**:
```python
# monitoring/__init__.py
_global_cancellation_manager: CancellationManager | None = None

def get_cancellation_manager() -> CancellationManager:
    global _global_cancellation_manager
    if _global_cancellation_manager is None:
        _global_cancellation_manager = CancellationManager()
    return _global_cancellation_manager
```

3. **在Agent中使用**:
```python
from .sdk_helper import execute_sdk_call

class YourAgent:
    async def run(self, prompt: str) -> SDKResult:
        return await execute_sdk_call(
            prompt=prompt,
            agent_name=self.__class__.__name__
        )
```

---

## 8. 最佳实践

### 8.1 提示词设计

```python
prompt = f"""@{file_path}

请执行以下任务：
{task_description}

要求：
1. 明确的成功标志
2. 结构化的输出格式
3. 错误时返回详细信息
"""
```

### 8.2 超时设置建议

| 任务类型 | 建议超时 |
|----------|----------|
| 简单查询 | 60-120秒 |
| 代码生成 | 300-600秒 |
| 复杂任务 | 1200-1800秒 |
| 批量处理 | 每文件 300秒 |

### 8.3 错误重试策略

```python
async def execute_with_retry(prompt: str, max_retries: int = 2) -> SDKResult:
    """带重试的SDK调用"""
    for attempt in range(max_retries + 1):
        result = await execute_sdk_call(prompt=prompt, agent_name="RetryAgent")
        
        if result.is_success():
            return result
        
        # 某些错误不重试
        if result.error_type in [SDKErrorType.CANCELLED, SDKErrorType.SDK_ERROR]:
            break
        
        # 指数退避
        if attempt < max_retries:
            await asyncio.sleep(2 ** attempt)
    
    return result
```

### 8.4 资源管理

1. **确保清理完成**: 使用 `track_sdk_execution` 上下文管理器
2. **避免资源泄漏**: 在finally块中关闭生成器
3. **监控活跃调用**: 定期检查 `get_active_calls_count()`

---

## 附录

### A. 文件结构

```
core/
├── cancellation_manager.py    # 取消管理器
├── sdk_executor.py            # SDK执行器
├── sdk_result.py              # 结果封装
└── API_USAGE.md               # API文档

agents/
├── sdk_helper.py              # 统一调用接口
└── base_agent.py              # Agent基类

monitoring/
├── __init__.py                # 全局管理器单例
└── resource_monitor.py        # 资源监控

sdk_wrapper.py                 # SafeClaudeSDK实现
```

### B. 依赖关系

```
claude_agent_sdk (外部)
    │
    ▼
sdk_wrapper.py (SafeClaudeSDK, SafeAsyncGenerator)
    │
    ▼
core/sdk_executor.py (SDKExecutor)
    │
    ├──▶ core/cancellation_manager.py (CancellationManager)
    │
    └──▶ core/sdk_result.py (SDKResult, SDKErrorType)
    │
    ▼
agents/sdk_helper.py (execute_sdk_call)
    │
    ▼
agents/* (SMAgent, DevAgent, QAAgent, etc.)
```

### C. 版本兼容

- Python: >= 3.10
- anyio: >= 4.0
- claude-agent-sdk: 最新版本

---

> **维护说明**: 本文档基于 epic_automation 项目的实际实现，如有更新请同步修改。

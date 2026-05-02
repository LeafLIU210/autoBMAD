# DocuSwarm 重构详细研究报告 - Part 3

> **版本**: 1.0
> **创建日期**: 2026-03-01
> **基于**: 
> - [DocuSwarm-重构详细研究报告.md](DocuSwarm-重构详细研究报告.md) (Part 1 - 核心架构)
> - [DocuSwarm-重构详细研究报告-Part2.md](DocuSwarm-重构详细研究报告-Part2.md) (Part 2 - 纯工具输出模式，需与本报告协调)
> **TDD 方案**: [TDD-05: Claude SDK Wrapper](../solution/TDD-05-SDKWrapper-Refactor.md)
> **聚焦领域**: kimi-agent-sdk 替换为 claude-agent-sdk + Kimi Code API

---

## 一、执行摘要

本报告详细分析将 DocuSwarm 中的 `kimi-agent-sdk` 替换为 `claude-agent-sdk` + Kimi Code API 的完整方案。

### 核心改造目标

1. **SDK 替换**: `kimi-agent-sdk` → `claude-agent-sdk`
2. **API 兼容**: 通过 Kimi Code API 的 OpenAI 兼容接口使用 Claude SDK
3. **环境变量**: 使用 `ANTHROPIC_BASE_URL="https://api.kimi.com/coding/"` 和 `ANTHROPIC_API_KEY`
4. **代码复用**: 借鉴 `epic_automation` 中成熟的 SDK 封装模式

### 改造收益

| 指标 | 改造前 | 改造后 |
|------|--------|--------|
| SDK 统一性 | 两套 SDK（kimi + claude） | 一套 SDK（claude） |
| 维护成本 | 双重学习曲线 | 单一学习曲线 |
| 工具系统 | CallableTool2（Kimi 专有） | 标准 Tool Use（通用） |
| 异步处理 | MessageAggregator（复杂） | ResultMessage（成熟） |
| 取消管理 | 无统一机制 | CancellationManager（成熟） |

---

## 二、SDK 对比分析

### 2.1 当前架构（kimi-agent-sdk）

**docuswarm 中的 kimi-agent-sdk 使用**:

```python
# 核心导入
from kimi_agent_sdk import (
    Config,
    Session,
    Message,
    WireMessage,
    ChatProviderError,
    ConfigError,
    MaxStepsReached,
    RunCancelled,
)
from kimi_agent_sdk._aggregator import MessageAggregator

# 会话创建
session = await Session.create(
    work_dir=work_dir,
    model="kimi-for-coding",
    yolo=True,
    config=Config(providers={...}, models={...}),
)

# 消息流处理
aggregator = MessageAggregator()
async for wire_msg in session.prompt(prompt):
    messages = aggregator.feed(wire_msg)
messages.extend(aggregator.flush())

# 工具定义
class CreateDeliverableTool(CallableTool2[CreateDeliverableParams]):
    name: str = "create_deliverable"
    params: type[CreateDeliverableParams] = CreateDeliverableParams
```

**关键特性**:
- Session API + Wire Protocol
- `MessageAggregator` 处理流式消息
- `CallableTool2[Params]` 工具定义模式
- `KaosPath` 路径类型依赖

### 2.2 目标架构（claude-agent-sdk）

**epic_automation 中的 claude-agent-sdk 使用**:

```python
# 核心导入
from claude_agent_sdk import (
    query,
    ResultMessage,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
)

# SDK 调用
options = ClaudeAgentOptions(
    permission_mode="bypassPermissions",
    cwd=str(Path.cwd()),
)

# 消息流处理
async for message in query(prompt=prompt, options=options):
    if isinstance(message, ResultMessage):
        if message.is_error:
            handle_error(message)
        else:
            result = message.result
```

**关键特性**:
- `query()` 函数式 API
- `ResultMessage` 终结消息
- `ClaudeAgentOptions` 配置
- 标准 `Path` 路径类型

### 2.3 API 兼容性映射

| kimi-agent-sdk | claude-agent-sdk | 说明 |
|----------------|------------------|------|
| `Session.create()` | `query()` | 会话 → 查询 |
| `session.prompt()` | `query()` 返回生成器 | 提示执行 |
| `WireMessage` | SDK 消息类型 | 流式消息 |
| `MessageAggregator` | 直接迭代 | 消息聚合 |
| `Message` | `ResultMessage` | 最终结果 |
| `CallableTool2[P]` | Tool Use Block | 工具调用 |
| `Config(providers=...)` | `ANTHROPIC_*` 环境变量 | 配置方式 |
| `KaosPath` | `Path` | 路径类型 |

---

## 三、环境变量配置方案

### 3.1 新增环境变量

**`.env` 文件配置**:

```env
# ===== Kimi Code API 配置（通过 Claude SDK 调用）=====
# 使用 ANTHROPIC_* 环境变量，不使用系统环境变量
ANTHROPIC_BASE_URL=https://api.kimi.com/coding/
ANTHROPIC_API_KEY=your-kimi-api-key-here

# ===== 模型配置 =====
# Kimi Code API 模型名称
KIMI_MODEL_NAME=kimi-for-coding

# ===== 超时配置 =====
# SDK 调用超时（秒）
SDK_TIMEOUT=1800
```

### 3.2 环境变量加载

**新增 `config.py` 中的加载逻辑**:

```python
"""DocuSwarm 配置模块 - 支持 claude-agent-sdk + Kimi Code API"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


@dataclass(frozen=True)
class DocuSwarmConfig:
    """DocuSwarm 配置（不可变）"""
    
    # Kimi Code API 配置（通过 ANTHROPIC_* 变量）
    anthropic_base_url: str
    anthropic_api_key: str
    model_name: str
    
    # 超时配置
    sdk_timeout: float
    
    # 数据库配置
    db_path: Path
    output_dir: Path
    log_level: str
    
    @classmethod
    def from_env(cls, env_file: Path | None = None) -> "DocuSwarmConfig":
        """从 .env 文件和环境变量加载配置"""
        
        # 加载 .env 文件（不覆盖已存在的系统环境变量）
        if env_file and env_file.exists():
            load_dotenv(env_file, override=False)
        else:
            # 尝试从当前目录和 autoBMAD/docuswarm 目录加载
            for path in [Path(".env"), Path("autoBMAD/docuswarm/.env")]:
                if path.exists():
                    load_dotenv(path, override=False)
                    break
        
        # 读取 ANTHROPIC_* 配置（优先级：.env > 环境变量 > 默认值）
        anthropic_base_url = os.getenv(
            "ANTHROPIC_BASE_URL", 
            "https://api.kimi.com/coding/"
        )
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
        # 验证必需配置
        if not anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required. "
                "Set it in .env file or as environment variable."
            )
        
        return cls(
            anthropic_base_url=anthropic_base_url,
            anthropic_api_key=anthropic_api_key,
            model_name=os.getenv("KIMI_MODEL_NAME", "kimi-for-coding"),
            sdk_timeout=float(os.getenv("SDK_TIMEOUT", "1800")),
            db_path=Path(os.getenv("DB_PATH", "docuswarm.db")),
            output_dir=Path(os.getenv("OUTPUT_DIR", "output")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


def load_config(env_file: Path | None = None) -> DocuSwarmConfig:
    """加载配置的便捷函数"""
    return DocuSwarmConfig.from_env(env_file)
```

### 3.3 环境变量优先级

```
优先级（从高到低）：
1. 系统环境变量（已设置的）
2. .env 文件（项目根目录）
3. .env 文件（autoBMAD/docuswarm 目录）
4. 代码默认值
```

---

## 四、SDK 封装层设计

> **完整实现**: [TDD-05: Claude SDK Wrapper](../solution/TDD-05-SDKWrapper-Refactor.md)

### 4.1 新增 `llm/claude_sdk_wrapper.py` (TDD-05)

借鉴 `epic_automation/sdk_wrapper.py` 的成熟模式：

```python
"""Claude SDK 封装层 - 统一的 SDK 调用接口

提供与 epic_automation 兼容的 SDK 调用模式，
通过 Kimi Code API 的 OpenAI 兼容接口工作。
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, TypeVar

import structlog

# Claude SDK 导入
try:
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        ThinkingBlock,
        ToolResultBlock,
        ToolUseBlock,
        UserMessage,
        query,
    )
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    query = None
    ResultMessage = None
    ClaudeAgentOptions = None
    AssistantMessage = None
    TextBlock = None
    ThinkingBlock = None
    ToolUseBlock = None
    ToolResultBlock = None
    UserMessage = None

logger = structlog.get_logger(__name__)


class SDKError(Exception):
    """SDK 执行错误"""
    pass


class SDKNotAvailableError(SDKError):
    """SDK 不可用"""
    pass


class SafeAsyncGenerator:
    """安全的异步生成器包装器 - 防止 cancel scope 跨任务错误"""
    
    def __init__(self, generator: AsyncIterator[Any]) -> None:
        self.generator = generator
        self._closed = False
    
    def __aiter__(self) -> "SafeAsyncGenerator":
        return self
    
    async def __anext__(self) -> Any:
        if self._closed:
            raise StopAsyncIteration
        try:
            return await self.generator.__anext__()
        except StopAsyncIteration:
            self._closed = True
            raise
    
    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        logger.debug("safe_generator_closed")


class ClaudeSDKWrapper:
    """Claude SDK 统一封装
    
    提供与 epic_automation 兼容的接口，通过 Kimi Code API 工作。
    
    Example:
        >>> wrapper = ClaudeSDKWrapper()
        >>> result = await wrapper.execute(
        ...     prompt="Create a market analysis report",
        ...     agent_name="analyst",
        ...     timeout=1800.0,
        ... )
        >>> if result.success:
        ...     print(result.content)
    """
    
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        permission_mode: str = "bypassPermissions",
    ) -> None:
        """初始化 SDK 封装
        
        Args:
            base_url: Kimi Code API base URL（默认从 ANTHROPIC_BASE_URL 读取）
            api_key: API key（默认从 ANTHROPIC_API_KEY 读取）
            permission_mode: 权限模式
        """
        self.base_url = base_url or os.getenv(
            "ANTHROPIC_BASE_URL", 
            "https://api.kimi.com/coding/"
        )
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.permission_mode = permission_mode
        
        self._logger = logger.bind(
            component="ClaudeSDKWrapper",
            base_url=self.base_url,
        )
    
    async def execute(
        self,
        prompt: str,
        agent_name: str = "docuswarm",
        timeout: float | None = 1800.0,
        cwd: str | Path | None = None,
    ) -> "SDKResult":
        """执行 SDK 调用
        
        Args:
            prompt: 提示词
            agent_name: Agent 名称（用于日志）
            timeout: 超时时间（秒）
            cwd: 工作目录
            
        Returns:
            SDKResult: 执行结果
        """
        if not SDK_AVAILABLE or query is None:
            return SDKResult(
                success=False,
                content=None,
                error="Claude Agent SDK not available",
                duration=0.0,
            )
        
        start_time = time.time()
        self._logger.info(
            "sdk_execute_start",
            agent_name=agent_name,
            prompt_length=len(prompt),
        )
        
        try:
            # 设置环境变量（claude-agent-sdk 通过环境变量读取配置）
            os.environ["ANTHROPIC_BASE_URL"] = self.base_url
            os.environ["ANTHROPIC_API_KEY"] = self.api_key
            
            # 创建选项
            options = ClaudeAgentOptions(
                permission_mode=self.permission_mode,
                cwd=str(cwd or Path.cwd()),
            )
            
            # 执行查询
            result_content = None
            messages: list[Any] = []
            
            generator = query(prompt=prompt, options=options)
            safe_gen = SafeAsyncGenerator(generator)
            
            try:
                async for message in safe_gen:
                    messages.append(message)
                    
                    # 检查是否为 ResultMessage
                    if ResultMessage and isinstance(message, ResultMessage):
                        if hasattr(message, "is_error") and message.is_error:
                            error_msg = getattr(message, "result", "Unknown error")
                            return SDKResult(
                                success=False,
                                content=None,
                                error=str(error_msg),
                                duration=time.time() - start_time,
                                messages=messages,
                            )
                        else:
                            result_content = getattr(message, "result", None)
                            break
            finally:
                await safe_gen.aclose()
            
            duration = time.time() - start_time
            
            if result_content is not None:
                self._logger.info(
                    "sdk_execute_success",
                    agent_name=agent_name,
                    duration=duration,
                    message_count=len(messages),
                )
                return SDKResult(
                    success=True,
                    content=str(result_content),
                    error=None,
                    duration=duration,
                    messages=messages,
                )
            else:
                self._logger.warning(
                    "sdk_execute_no_result",
                    agent_name=agent_name,
                    duration=duration,
                )
                return SDKResult(
                    success=False,
                    content=None,
                    error="No ResultMessage received",
                    duration=duration,
                    messages=messages,
                )
                
        except asyncio.CancelledError:
            self._logger.warning("sdk_execute_cancelled", agent_name=agent_name)
            return SDKResult(
                success=False,
                content=None,
                error="Execution cancelled",
                duration=time.time() - start_time,
            )
        except Exception as e:
            self._logger.error(
                "sdk_execute_error",
                agent_name=agent_name,
                error=str(e),
            )
            return SDKResult(
                success=False,
                content=None,
                error=str(e),
                duration=time.time() - start_time,
            )


@dataclass
class SDKResult:
    """SDK 执行结果"""
    
    success: bool
    content: str | None
    error: str | None
    duration: float
    messages: list[Any] = field(default_factory=list)
    
    def is_success(self) -> bool:
        """检查是否成功"""
        return self.success and self.content is not None


from dataclasses import dataclass, field
```

### 4.2 替换 `llm/session_manager.py` (TDD-05)

将 `KimiSessionManager` 替换为基于 `ClaudeSDKWrapper` 的实现：

```python
"""Session Manager - 基于 Claude SDK 的会话管理

替代原有的 KimiSessionManager，使用 claude-agent-sdk 通过 Kimi Code API 工作。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import structlog

from autoBMAD.docuswarm.llm.claude_sdk_wrapper import (
    ClaudeSDKWrapper,
    SDKResult,
    SDK_AVAILABLE,
)

logger = structlog.get_logger(__name__)


class SessionManager:
    """会话管理器 - 基于 Claude SDK
    
    提供与原 KimiSessionManager 兼容的接口。
    
    Example:
        >>> manager = SessionManager(work_dir=Path.cwd())
        >>> result = await manager.single_prompt("Hello!")
        >>> print(result.content)
    """
    
    def __init__(
        self,
        work_dir: Path | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """初始化会话管理器
        
        Args:
            work_dir: 工作目录
            base_url: API base URL（默认从环境变量读取）
            api_key: API key（默认从环境变量读取）
        """
        self._work_dir = work_dir or Path.cwd()
        self._sdk = ClaudeSDKWrapper(
            base_url=base_url,
            api_key=api_key,
        )
        self._logger = logger.bind(
            component="SessionManager",
            work_dir=str(self._work_dir),
        )
    
    @property
    def work_dir(self) -> Path:
        """获取工作目录"""
        return self._work_dir
    
    @property
    def config(self) -> Any:
        """获取配置（兼容性）"""
        return {
            "base_url": self._sdk.base_url,
            "work_dir": str(self._work_dir),
        }
    
    async def single_prompt(
        self,
        prompt: str,
        mode: str = "agent",
        yolo: bool = True,
        agent_name: str = "docuswarm",
        timeout: float | None = 1800.0,
    ) -> SDKResult:
        """执行单次提示（兼容原 single_prompt 接口）
        
        Args:
            prompt: 提示词
            mode: 模式（兼容性参数，实际不使用）
            yolo: 自动批准（兼容性参数，实际不使用）
            agent_name: Agent 名称
            timeout: 超时时间
            
        Returns:
            SDKResult: 执行结果
        """
        self._logger.info(
            "single_prompt_start",
            prompt_length=len(prompt),
            mode=mode,
            agent_name=agent_name,
        )
        
        result = await self._sdk.execute(
            prompt=prompt,
            agent_name=agent_name,
            timeout=timeout,
            cwd=self._work_dir,
        )
        
        self._logger.info(
            "single_prompt_complete",
            success=result.success,
            duration=result.duration,
        )
        
        return result
    
    async def execute_with_tools(
        self,
        prompt: str,
        tools: list[Any] | None = None,
        agent_name: str = "docuswarm",
        timeout: float | None = 1800.0,
    ) -> SDKResult:
        """执行带工具的提示
        
        Args:
            prompt: 提示词（应包含工具调用指令）
            tools: 工具列表（用于提示构建，实际工具由 SDK 处理）
            agent_name: Agent 名称
            timeout: 超时时间
            
        Returns:
            SDKResult: 执行结果
        """
        # 构建包含工具信息的提示
        if tools:
            tool_descriptions = "\n".join(
                f"- {t.name}: {t.description}" 
                for t in tools 
                if hasattr(t, 'name') and hasattr(t, 'description')
            )
            full_prompt = f"""Available tools:
{tool_descriptions}

{prompt}"""
        else:
            full_prompt = prompt
        
        return await self.single_prompt(
            prompt=full_prompt,
            agent_name=agent_name,
            timeout=timeout,
        )
    
    async def close(self) -> None:
        """关闭会话管理器（兼容性）"""
        self._logger.debug("session_manager_closed")
    
    async def __aenter__(self) -> "SessionManager":
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        await self.close()
```

---

## 五、工具系统改造

### 5.1 工具定义变更

**从 `CallableTool2[Params]` 到标准函数**:

```python
# 原有方式（kimi-agent-sdk）
class CreateDeliverableTool(CallableTool2[CreateDeliverableParams]):
    name: str = "create_deliverable"
    params: type[CreateDeliverableParams] = CreateDeliverableParams
    
    async def __call__(self, params: CreateDeliverableParams) -> ToolReturnValue:
        ...

# 新方式（claude-agent-sdk 兼容）
async def create_deliverable(title: str, content: str, metadata: dict | None = None) -> str:
    """创建交付物文档
    
    Args:
        title: 文档标题
        content: 文档内容（Markdown 格式）
        metadata: 额外元数据
        
    Returns:
        成功消息或错误描述
    """
    ...
```

### 5.2 工具注册方式变更

**claude-agent-sdk 通过 Agent 文件定义工具**:

```yaml
# agents/configs/docuswarm_agent.yaml
tools:
  - name: create_deliverable
    description: Create a deliverable document in Markdown format
    parameters:
      title:
        type: string
        description: Document title
      content:
        type: string
        description: Document content in Markdown
      metadata:
        type: object
        description: Additional metadata
        required: false
```

### 5.3 工具文件改造清单

| 原文件 | 改造内容 |
|--------|---------|
| `tools/create_deliverable.py` | 移除 `CallableTool2`，改为标准 async 函数 |
| `tools/create_document_set.py` | 移除 `CallableTool2`，改为标准 async 函数 |
| `tools/read_docs_file.py` | 移除 `CallableTool2`，改为标准 async 函数 |
| `tools/update_docs_file.py` | 移除 `CallableTool2`，改为标准 async 函数 |
| `tools/list_docs_files.py` | 移除 `CallableTool2`，改为标准 async 函数 |
| `tools/update_context.py` | 移除 `CallableTool2`，改为标准 async 函数 |

---

## 六、Agent 改造

### 6.1 IndependentAgent 改造

```python
# 原有导入
from kimi_agent_sdk import Message
from kimi_agent_sdk._aggregator import MessageAggregator

# 新导入
from autoBMAD.docuswarm.llm.session_manager import SessionManager, SDKResult

# 原有调用方式
async def _call_llm(self, user_message: str) -> list[Message]:
    session = await self.session_manager.create_session(mode="agent", yolo=True)
    aggregator = MessageAggregator()
    async for wire_msg in session.prompt(full_prompt):
        for msg in aggregator.feed(wire_msg):
            messages.append(msg)
    return aggregator.flush()

# 新调用方式
async def _call_llm(self, user_message: str) -> SDKResult:
    result = await self.session_manager.single_prompt(
        prompt=user_message,
        agent_name=f"independent-{self.node_id}",
        timeout=1800.0,
    )
    return result
```

### 6.2 EvaluatorAgent 改造

```python
# 原有方式
messages = await self.session_manager.single_prompt(prompt, mode="thinking", yolo=True)

# 新方式
result = await self.session_manager.single_prompt(
    prompt=prompt,
    agent_name="evaluator",
    timeout=600.0,
)
if result.success:
    evaluation_text = result.content
```

---

## 七、依赖变更

### 7.1 pyproject.toml 修改

```toml
[project]
dependencies = [
    # 移除 kimi-agent-sdk
    # "kimi-agent-sdk >= 0.0.5, < 0.1.0",
    
    # 新增 claude-agent-sdk
    "claude-agent-sdk >= 0.1.38",
    
    # 其他依赖保持不变
    "langgraph >= 0.2.50, < 0.3.0",
    "pydantic >= 2.0.0, < 3.0.0",
    "structlog >= 24.0.0",
    "aiofiles >= 24.0.0",
    "aiosqlite >= 0.19.0",
    "python-dotenv >= 1.0.0",
]
```

### 7.2 requirements.txt 修改

```
# SDK
claude-agent-sdk>=0.1.38
# kimi-agent-sdk>=0.0.5  # 移除

# 其他依赖
langgraph>=0.2.50
pydantic>=2.0.0
structlog>=24.0.0
aiofiles>=24.0.0
aiosqlite>=0.19.0
python-dotenv>=1.0.0
anyio>=4.0.0  # claude-agent-sdk 依赖
```

---

## 八、实施路线图

> **与 Part 2 的协调**: 
> - 本报告 Phase 3（工具系统改造）应与 Part 2 Phase 2（纯工具输出模式）**同步协调实施**
> - 本报告 Phase 4（Agent 改造）应与 Part 2 Phase 1（移除提问 Agent）协调，确保提问逻辑完全移除

### 8.1 Phase 1: 环境配置（0.5 天）

| 步骤 | 任务 | 影响文件 |
|------|------|---------|
| 1.1 | 创建 `.env` 模板 | `.env.example` |
| 1.2 | 修改 `config.py` 支持 `ANTHROPIC_*` | `config.py` |
| 1.3 | 更新 `CONFIGURATION.md` | `CONFIGURATION.md` |

### 8.2 Phase 2: SDK 封装层（1 天）

> **TDD 方案**: [TDD-05](../solution/TDD-05-SDKWrapper-Refactor.md)

| 步骤 | 任务 | 影响文件 | TDD 参考 |
|------|------|---------|---------|
| 2.1 | 创建 `claude_sdk_wrapper.py` | `llm/claude_sdk_wrapper.py` | TDD-05 第3节 |
| 2.2 | 替换 `session_manager.py` | `llm/session_manager.py` | TDD-05 第3节 |
| 2.3 | 编写单元测试 | `tests/unit/test_claude_sdk_wrapper.py` | TDD-05 第3节 |

### 8.3 Phase 3: 工具系统改造（1 天）- 与 Part 2 Phase 2 协调

| 步骤 | 任务 | 影响文件 | 与 Part 2 协调 |
|------|------|---------|---------------|
| 3.1 | 改造 `create_deliverable.py` | `tools/create_deliverable.py` | 确保输出可被 `tool_result_extractor.py` 提取（Part 2 第3.2.2节） |
| 3.2 | 改造其他工具文件 | `tools/*.py` | 同上 |
| 3.3 | 创建 `tool_result_extractor.py` | `tools/tool_result_extractor.py` | 从 Part 2 第3.2.2节实现，适配 claude-agent-sdk 消息格式 |
| 3.4 | 创建 Agent 配置文件 | `agents/configs/*.yaml` | - |
| 3.5 | 编写工具测试 | `tests/unit/test_tools.py` | - |

### 8.4 Phase 4: Agent 改造（1.5 天）

| 步骤 | 任务 | 影响文件 |
|------|------|---------|
| 4.1 | 改造 `IndependentAgent` | `agents/independent.py` |
| 4.2 | 改造 `EvaluatorAgent` | `agents/evaluator.py` |
| 4.3 | 更新 `orchestrator.py` | `pipeline/orchestrator.py` |
| 4.4 | 更新 `main.py` | `main.py` |
| 4.5 | 编写集成测试 | `tests/integration/` |

### 8.5 Phase 5: 依赖和文档更新（0.5 天）

| 步骤 | 任务 | 影响文件 |
|------|------|---------|
| 5.1 | 更新 `pyproject.toml` | `pyproject.toml` |
| 5.2 | 更新 `requirements.txt` | `requirements.txt` |
| 5.3 | 更新 `requirements-dev.txt` | `requirements-dev.txt` |
| 5.4 | 更新 `README.md` | `README.md` |

---

## 九、影响范围汇总

### 9.1 文件修改清单

| 文件 | 改动类型 | 改动规模 |
|------|---------|---------|
| `llm/session_manager.py` | 重写 | ~550 → ~150 行 |
| `llm/claude_sdk_wrapper.py` | 新增 | ~300 行 |
| `agents/independent.py` | 修改 | ~100 行改动 |
| `agents/evaluator.py` | 修改 | ~50 行改动 |
| `tools/tool_result_extractor.py` | 新增 | ~280 行（从 Part 2 第3.2.2节实现） |
| `tools/create_deliverable.py` | 重写 | ~96 → ~60 行 |
| `tools/create_document_set.py` | 重写 | ~269 → ~150 行 |
| `tools/read_docs_file.py` | 重写 | ~119 → ~70 行 |
| `tools/update_docs_file.py` | 重写 | ~154 → ~90 行 |
| `tools/list_docs_files.py` | 重写 | ~123 → ~70 行 |
| `tools/update_context.py` | 重写 | ~61 → ~40 行 |
| `config.py` | 修改 | ~50 行改动 |
| `pipeline/orchestrator.py` | 修改 | ~30 行改动 |
| `main.py` | 修改 | ~20 行改动 |

### 9.2 移除的依赖

```
- kimi-agent-sdk
- kaos (KaosPath 依赖)
- kimi_cli (Wire 协议依赖)
```

### 9.3 新增的依赖

```
+ claude-agent-sdk >= 0.1.38
+ anyio >= 4.0.0 (claude-agent-sdk 依赖)
```

---

## 十、风险与缓解

| 风险 | 可能性 | 影响 | 缓解策略 |
|------|--------|------|---------|
| Kimi Code API 与 Claude SDK 不完全兼容 | 中 | 高 | 先在隔离环境测试 API 兼容性 |
| 工具系统行为差异 | 中 | 中 | 保留工具单元测试，逐一验证 |
| 性能差异 | 低 | 中 | 基准测试对比 |
| 流式消息处理差异 | 中 | 中 | 借鉴 epic_automation 成熟模式 |

---

## 十一、验收标准

### 11.1 功能验收

```bash
# 1. 环境变量配置
export ANTHROPIC_BASE_URL="https://api.kimi.com/coding/"
export ANTHROPIC_API_KEY="your-key"

# 2. 启动管道测试
python -m autoBMAD.docuswarm start -c test_context.md

# 3. 验证输出
ls output/pipeline-*/
# 应生成 5 个节点的 deliverable 文件
```

### 11.2 质量验收

```bash
# 类型检查
basedpyright autoBMAD/docuswarm/

# 代码风格
ruff check autoBMAD/docuswarm/

# 测试覆盖
pytest tests/ -v --cov=autoBMAD/docuswarm --cov-report=term-missing
# 覆盖率 >= 80%
```

---

> **本报告为 DocuSwarm 重构详细研究报告的第三部分**
> - **Part 1**: [DocuSwarm-重构详细研究报告.md](DocuSwarm-重构详细研究报告.md) - 核心架构问题与 12-Factor 对齐
> - **Part 2**: [DocuSwarm-重构详细研究报告-Part2.md](DocuSwarm-重构详细研究报告-Part2.md) - 提问 Agent 移除 + 纯工具输出 + "@" 路径注入
> - **Part 3**: 本文档 - SDK 替换 (kimi-agent-sdk → claude-agent-sdk + Kimi Code API)
> 
> **与 Part 2 的协调**: 
> - 本报告第5节的工具系统改造应与 Part 2 的纯工具输出模式（第3节）同步实施
> - 建议顺序：先完成本报告 Phase 1-2（环境配置 + SDK 封装层），再与 Part 2 Phase 2 协同改造工具系统

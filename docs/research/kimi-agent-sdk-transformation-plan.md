# DocuSwarm 项目 kimi-agent-sdk 改造方案研究报告

**版本**: 1.1
**日期**: 2026-02-20
**范围**: docuswarm 核心多代理编排系统从 KimiClient 迁移至 kimi-agent-sdk

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [现有架构分析](#2-现有架构分析)
3. [kimi-agent-sdk 能力矩阵](#3-kimi-agent-sdk-能力矩阵)
4. [架构差异对比](#4-架构差异对比)
5. [改造方案总体设计](#5-改造方案总体设计)
6. [模块级改造细节](#6-模块级改造细节)
7. [自定义工具迁移](#7-自定义工具迁移)
8. [会话管理改造](#8-会话管理改造)
9. [取消机制改造](#9-取消机制改造)
10. [审批与安全控制](#10-审批与安全控制)
11. [风险评估与缓解](#11-风险评估与缓解)
12. [实施路线图](#12-实施路线图)
13. [附录](#13-附录)

---

## 1. 执行摘要

### 1.1 改造目标

将 docuswarm 核心的 LLM 调用层从 `KimiClient`（httpx 直连 REST API）迁移至 **kimi-agent-sdk**，实现：

- **原生能力利用**: 利用 kimi-agent-sdk 的 Session 持久化、取消机制、审批系统、自定义工具
- **流式消息处理**: Wire 流式消息替代单次 req/res，降低首字延迟
- **会话持久化**: `Session.create()` / `Session.resume()` 支持多轮对话和中断恢复
- **原生工具系统**: `CallableTool2` + Pydantic 替代手动 JSON Schema 工具定义
- **原生取消支持**: `session.cancel()` + `asyncio.Event` 替代无取消能力的 httpx 调用

### 1.2 核心结论

| 维度 | 现有架构 | kimi-agent-sdk 改造后 |
|------|---------|---------------------|
| **LLM 调用** | httpx 直连 Kimi API (REST) | SDK 封装的 Kimi CLI Wire 协议 |
| **工具调用** | 手动 JSON Schema + 响应解析 | `CallableTool2` Pydantic 原生 |
| **会话管理** | 无持久化（每次独立 HTTP 请求） | `Session.create()` / `Session.resume()` |
| **取消机制** | 无（仅 httpx 超时） | `session.cancel()` + `asyncio.Event` |
| **审批控制** | 无（agent mode 全自动） | `ApprovalRequest` + handler |
| **消息流** | 单次请求/响应 | Wire 流式消息 + `MessageAggregator` |
| **SDK 依赖** | httpx | kimi-agent-sdk (kimi-cli + kosong) |

### 1.3 改造影响范围

```
高影响（核心重构）:
  docuswarm/llm/client.py        → 替换为 SDK Session wrapper
  docuswarm/agents/base.py       → 适配 SDK Session API
  docuswarm/agents/independent.py → 工具调用改造
  docuswarm/agents/evaluator.py  → 消息流处理改造

中影响（适配调整）:
  docuswarm/llm/tools.py         → CallableTool2 迁移
  docuswarm/llm/config.py        → SDK Config 适配

低影响（配置变更）:
  pyproject.toml                 → 依赖替换
  docuswarm/llm/rate_limit.py    → SDK 内置限流可能替代
  docuswarm/llm/retry.py         → SDK 内置重试可能替代
```

---

## 2. 现有架构分析

### 2.1 KimiClient — LLM 调用核心

**文件**: `docuswarm/llm/client.py`

当前架构使用 `httpx.AsyncClient` 直连 Kimi API：

```
KimiClient
├── httpx.AsyncClient → https://api.moonshot.cn/v1/chat/completions
├── TokenBucketRateLimiter (200 RPM, 20 并发)
├── RetryHandler (3 次, 指数退避)
└── 三种 ChatMode: INSTANT / THINKING / AGENT
```

**调用路径**:
```
BaseAgent.execute()
  → IndependentAgent._call_llm() / EvaluatorAgent._call_llm()
    → KimiClient.chat(messages, mode, tools)
      → _rate_limiter.acquire()
      → _retry_handler.execute(_send_request)
        → httpx.post("/chat/completions", json=payload)
      → _parse_response()
    ← ChatResponse(content, usage, model, finish_reason)
```

**关键问题**:
- 无会话持久化：每次调用都是独立 HTTP 请求，无法跨调用保持对话上下文
- 无流式支持：等待完整响应返回，首字延迟高
- 手动工具调用管理：JSON Schema 手写，tool_calls 响应需手动解析和执行
- 无原生取消支持：仅依赖 httpx 超时，无法中途取消正在执行的推理

### 2.2 工具定义 — 手动 JSON Schema

**文件**: `docuswarm/llm/tools.py`

当前工具以手动 JSON Schema 定义：

```python
DOCUSWARM_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_deliverable",
            "description": "...",
            "parameters": {
                "type": "object",
                "properties": {...},
                "required": [...]
            }
        }
    }
]
```

**问题**:
- JSON Schema 手写，易出错且无类型安全
- 无 Pydantic 参数验证
- 工具执行逻辑散落在 Agent 代码中，SDK 无法自动调度

### 2.3 Agent 层 — BaseAgent / IndependentAgent / EvaluatorAgent

**文件**: `docuswarm/agents/base.py`, `independent.py`, `evaluator.py`

```
BaseAgent(ABC)
├── config: AgentConfig
├── llm: KimiClient         ← 依赖注入
├── logger: BoundLogger
└── execute(context) → dict  ← 抽象方法

IndependentAgent(BaseAgent)
├── _call_llm(): ChatMode.AGENT + tools
├── 输出: deliverable + questions + private_reasoning
└── 工具: create_deliverable, update_context

EvaluatorAgent(BaseAgent)
├── _call_llm(): ChatMode.THINKING (无 tools)
├── 输入: subject_context + deliverable (上下文隔离)
├── 输出: verdict + alignment_score + issues + suggestions
└── 保护: 拒绝 private_reasoning 字段
```

---

## 3. kimi-agent-sdk 能力矩阵

### 3.1 API 层级

| API 层级 | 类型 | 用途 | DocuSwarm 映射 |
|---------|------|------|---------------|
| **`prompt()`** | 高级 | 单次任务，自动管理会话生命周期 | Evaluator 评估（单次推理） |
| **`Session.create()`** | 中级 | 多轮对话，持久化 | Independent Agent（迭代推理） |
| **`Session.resume()`** | 中级 | 恢复已有会话 | Pipeline 中断恢复 |
| **Wire Messages** | 低级 | 原始消息流 | 细粒度控制需求 |

### 3.2 核心能力

```
kimi-agent-sdk
├── Session 生命周期
│   ├── create() → 创建新会话
│   ├── resume() → 恢复已有会话（通过 session_id）
│   ├── prompt() → 发送提示并获取 WireMessage 流
│   ├── cancel() → 取消当前 prompt（asyncio.Event）
│   └── close() → 释放资源（async context manager）
│
├── 消息系统
│   ├── WireMessage → 底层 Wire 消息
│   ├── Message → 聚合后的高级消息
│   ├── MessageAggregator → Wire → Message 转换
│   ├── ContentPart → 文本/图片/音频/视频
│   └── ToolCall / ToolResult → 工具调用追踪
│
├── 自定义工具
│   ├── CallableTool2 → Pydantic 基类
│   ├── ToolOk / ToolError → 标准返回类型
│   └── agent_file (YAML) → 工具注册
│
├── 审批系统
│   ├── ApprovalRequest → 审批请求（id, action, description, display）
│   ├── resolve("approve") → 批准单次
│   ├── resolve("approve_for_session") → 批准整个会话
│   └── resolve("reject") → 拒绝
│
├── 配置
│   ├── Config → 全局配置
│   ├── MCPConfig → MCP 服务器配置
│   ├── model → 模型选择
│   ├── thinking → 推理模式
│   └── yolo → 自动批准模式
│
└── 异常体系
    ├── SessionStateError → 会话状态错误
    ├── PromptValidationError → 配置验证错误
    ├── RunCancelled → 取消异常
    ├── MaxStepsReached → 步骤上限
    └── ChatProviderError → API 错误（含 429/timeout/5xx）
```

### 3.3 依赖要求

```toml
# kimi-agent-sdk Python SDK
requires-python = ">=3.12"
dependencies = [
    "kimi-cli>=1.12.0,<1.13.0",  # Kimi CLI 运行时
    "kosong>=0.42.0,<0.43.0",    # 消息和工具类型库
]
```

**注意**: kimi-agent-sdk 通过 kimi-cli 进程（`--wire` 模式）与 Kimi 后端通信，而非直接 HTTP 调用。这意味着 SDK 内部已处理连接管理、重试、消息序列化等底层细节。

---

## 4. 架构差异对比

### 4.1 调用模型差异

```
现有架构:
┌─────────┐     ┌──────────┐     ┌────────────┐
│ Agent   │────→│KimiClient│────→│ Kimi API   │
│         │     │ (httpx)  │     │ (HTTP/REST)│
└─────────┘     └──────────┘     └────────────┘
                     ↑
            手动管理: 消息格式化、工具Schema、
            速率限制、重试、响应解析

kimi-agent-sdk 架构:
┌─────────┐     ┌──────────┐     ┌────────────┐     ┌────────────┐
│ Agent   │────→│ Session  │────→│ KimiCLI    │────→│ Kimi API   │
│         │     │ (SDK)    │     │ (Wire)     │     │            │
└─────────┘     └──────────┘     └────────────┘     └────────────┘
                     ↑
            SDK 管理: 消息聚合、工具执行、
            审批处理、会话持久化、取消
```

### 4.2 功能映射表

| docuswarm 现有功能 | 现有实现 | kimi-agent-sdk 对应 | 改造策略 |
|------------------|---------|-------------------|---------|
| LLM 调用 | `KimiClient.chat()` | `Session.prompt()` / `prompt()` | 替换 |
| 工具定义 | JSON Schema 手写 | `CallableTool2` + Pydantic | 迁移 |
| 工具执行 | Agent 内手动解析 tool_calls | SDK 自动调度 + 自动返回 ToolResult | 替换 |
| 速率限制 | `TokenBucketRateLimiter` | SDK 内置 / 保留 | 评估 |
| 重试逻辑 | `RetryHandler` | SDK 内置 (`max_retries_per_step`) | 替换 |
| 取消机制 | 无 | `session.cancel()` | 新增 |
| 会话管理 | 无 | `Session.create/resume` | 新增 |
| 消息流 | 单次 req/res | Wire 流式 + MessageAggregator | 改造 |
| 审批控制 | 无 | `ApprovalRequest` handler | 新增 |
| 错误处理 | 手动 HTTP 状态码检查 | SDK 异常体系（类型化异常） | 替换 |
| 三种模式 | `ChatMode` 枚举 | `model` + `thinking` 参数 | 适配 |
| 上下文隔离 | `ContextFilter` | 保留（业务层逻辑） | 不变 |

### 4.3 不可直接映射的功能

| 功能 | 原因 | 处理方案 |
|------|------|---------|
| `TokenBucketRateLimiter` | SDK 内部可能有自己的限流 | 保留作为外层防护，或移除后依赖 SDK |
| `ChatMode.INSTANT/THINKING/AGENT` | SDK 通过 `model` + `thinking` 参数控制 | 创建模式映射层 |
| `ChatResponse` 数据结构 | SDK 使用 `Message` / `WireMessage` | 创建适配层或直接使用 SDK 类型 |

---

## 5. 改造方案总体设计

### 5.1 架构目标

```
改造后架构:

┌─────────────────────────────────────────────────┐
│                DocuSwarm Application             │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Analyst  │  │   PM     │  │   UX     │ ... │  ← BMAD 节点
│  │  Node    │  │  Node    │  │  Node    │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │              │              │           │
│  ┌────▼──────────────▼──────────────▼─────┐     │
│  │         DualAgentNode                  │     │  ← 双代理编排
│  │  ┌─────────────┐  ┌─────────────┐     │     │
│  │  │Independent  │  │ Evaluator   │     │     │
│  │  │   Agent     │  │   Agent     │     │     │
│  │  └──────┬──────┘  └──────┬──────┘     │     │
│  └─────────┼────────────────┼────────────┘     │
│            │                │                   │
│  ┌─────────▼────────────────▼────────────┐     │
│  │      KimiSessionManager (新)          │     │  ← SDK 适配层
│  │  ┌────────────┐  ┌────────────────┐   │     │
│  │  │  Session   │  │   prompt()     │   │     │
│  │  │ (多轮持久) │  │  (单次评估)    │   │     │
│  │  └────────────┘  └────────────────┘   │     │
│  │  ┌────────────┐  ┌────────────────┐   │     │
│  │  │  Custom    │  │   Approval     │   │     │
│  │  │  Tools     │  │   Handler      │   │     │
│  │  └────────────┘  └────────────────┘   │     │
│  └───────────────────────────────────────┘     │
│                      │                          │
└──────────────────────┼──────────────────────────┘
                       │
              ┌────────▼────────┐
              │ kimi-agent-sdk  │
              │  (Session/Wire) │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │   Kimi CLI      │
              │  (Wire Protocol)│
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  Kimi K2.5 API  │
              └─────────────────┘
```

### 5.2 分层设计

**Layer 1: SDK 适配层** (新增)
- `KimiSessionManager`: 管理 Session 生命周期，替代 `KimiClient`
- `DocuSwarmApprovalHandler`: 审批策略
- `ModeMapper`: ChatMode → SDK 参数映射

**Layer 2: Agent 适配层** (修改)
- `BaseAgent`: 注入 `KimiSessionManager` 替代 `KimiClient`
- `IndependentAgent`: 使用 `Session` 多轮 + 自定义工具
- `EvaluatorAgent`: 使用 `prompt()` 单次 + thinking 模式

**Layer 3: 工具层** (重写)
- `CreateDeliverableTool(CallableTool2)`: 原生 Pydantic 工具
- `UpdateContextTool(CallableTool2)`: 原生 Pydantic 工具

---

## 6. 模块级改造细节

### 6.1 KimiClient → KimiSessionManager

**现有**: `docuswarm/llm/client.py` (KimiClient)
**改造后**: `docuswarm/llm/session_manager.py` (KimiSessionManager)

```python
# 改造后的 KimiSessionManager 设计
class KimiSessionManager:
    """
    基于 kimi-agent-sdk 的会话管理器。
    替代原有的 KimiClient，提供 Session 生命周期管理。
    """

    def __init__(
        self,
        work_dir: KaosPath | None = None,
        agent_file: Path | None = None,
        config: Config | Path | None = None,
    ) -> None:
        self._work_dir = work_dir or KaosPath.cwd()
        self._agent_file = agent_file
        self._config = config
        self._active_sessions: dict[str, Session] = {}

    async def create_session(
        self,
        session_id: str | None = None,
        mode: str = "agent",       # "instant" | "thinking" | "agent"
        yolo: bool = False,
        max_steps: int | None = None,
    ) -> Session:
        """创建新 Session（对应原 KimiClient.chat 的初始化）"""
        session = await Session.create(
            work_dir=self._work_dir,
            session_id=session_id,
            config=self._config,
            model="kimi",
            thinking=(mode == "thinking"),
            yolo=yolo,
            agent_file=self._agent_file,
            max_steps_per_turn=max_steps,
        )
        if session_id:
            self._active_sessions[session_id] = session
        return session

    async def resume_session(self, session_id: str) -> Session | None:
        """恢复已有 Session"""
        return await Session.resume(
            work_dir=self._work_dir,
            session_id=session_id,
            config=self._config,
            agent_file=self._agent_file,
        )

    async def single_prompt(
        self,
        user_input: str,
        mode: str = "instant",
        yolo: bool = True,
        approval_handler: ApprovalHandlerFn | None = None,
    ) -> list[Message]:
        """单次调用（对应原 KimiClient.chat）"""
        messages = []
        async for msg in prompt(
            user_input,
            work_dir=self._work_dir,
            config=self._config,
            model="kimi",
            thinking=(mode == "thinking"),
            yolo=yolo,
            approval_handler_fn=approval_handler,
            agent_file=self._agent_file,
        ):
            messages.append(msg)
        return messages

    async def close_all(self) -> None:
        """关闭所有活跃 Session"""
        for session in self._active_sessions.values():
            await session.close()
        self._active_sessions.clear()
```

### 6.2 BaseAgent 改造

**现有**: 注入 `KimiClient`
**改造后**: 注入 `KimiSessionManager`

```python
# 改造后的 BaseAgent
class BaseAgent(ABC):
    def __init__(
        self,
        config: AgentConfig,
        session_manager: KimiSessionManager,  # 替代 KimiClient
    ) -> None:
        self.config = config
        self.session_manager = session_manager  # 替代 self.llm
        self.logger = structlog.get_logger().bind(agent=self.__class__.__name__)

    @abstractmethod
    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        pass
```

### 6.3 IndependentAgent 改造

**关键变化**: 使用 `Session` 多轮对话 + 自定义工具自动调度

```python
# 改造后的 IndependentAgent._call_llm
class IndependentAgent(BaseAgent):
    async def _call_llm(
        self,
        user_message: str,
        session_id: str | None = None,
    ) -> IndependentOutput:
        """使用 Session API 执行多轮推理"""

        # 创建带工具的 Session
        session = await self.session_manager.create_session(
            session_id=session_id,
            mode="agent",
            yolo=True,  # Independent Agent 自动批准工具调用
            max_steps=20,
        )

        try:
            async with session:
                # 收集 Wire 消息
                aggregator = MessageAggregator()
                async for wire_msg in session.prompt(user_message):
                    if isinstance(wire_msg, ApprovalRequest):
                        wire_msg.resolve("approve")
                        continue
                    for message in aggregator.feed(wire_msg):
                        self._process_message(message)

                # flush 最终消息
                for message in aggregator.flush():
                    self._process_message(message)

        except MaxStepsReached:
            self.logger.warning("max_steps_reached")
        except RunCancelled:
            self.logger.info("run_cancelled")

        return self._build_output()
```

### 6.4 EvaluatorAgent 改造

**关键变化**: 使用 `prompt()` 高级 API + thinking 模式

```python
# 改造后的 EvaluatorAgent._call_llm
class EvaluatorAgent(BaseAgent):
    async def _call_llm(
        self,
        subject_context: str,
        deliverable: dict[str, Any],
    ) -> EvaluatorOutput:
        """使用 prompt() 高级 API 执行评估"""

        # 上下文隔离验证（保留）
        # ... existing isolation checks ...

        # 构建评估提示
        eval_prompt = self._format_evaluation_prompt(
            subject_context, deliverable
        )

        # 使用 thinking 模式进行深度评估
        messages = await self.session_manager.single_prompt(
            user_input=eval_prompt,
            mode="thinking",
            yolo=True,
        )

        # 解析评估结果
        return self._parse_evaluation(messages)
```

---

## 7. 自定义工具迁移

### 7.1 现有工具 → CallableTool2

**现有** (`docuswarm/llm/tools.py`): 手动 JSON Schema

**改造后**: Pydantic + CallableTool2

```python
# 改造后: docuswarm/tools/create_deliverable.py
from pydantic import BaseModel, Field
from kimi_agent_sdk import CallableTool2, ToolOk, ToolError, ToolReturnValue


class CreateDeliverableParams(BaseModel):
    """可交付物创建参数"""
    title: str = Field(description="可交付物标题")
    content: str = Field(description="可交付物内容（Markdown格式）")
    metadata: dict = Field(default_factory=dict, description="附加元数据")


class CreateDeliverableTool(CallableTool2):
    """创建节点可交付物文档"""
    name: str = "create_deliverable"
    description: str = "创建节点可交付物文档，包含标题、内容和元数据"
    params: type[CreateDeliverableParams] = CreateDeliverableParams

    def __init__(self, output_handler):
        super().__init__()
        self._output_handler = output_handler

    async def __call__(self, params: CreateDeliverableParams) -> ToolReturnValue:
        try:
            self._output_handler.save_deliverable(
                title=params.title,
                content=params.content,
                metadata=params.metadata,
            )
            return ToolOk(output=f"Deliverable '{params.title}' created successfully")
        except Exception as exc:
            return ToolError(
                output="",
                message=str(exc),
                brief="Failed to create deliverable",
            )
```

```python
# 改造后: docuswarm/tools/update_context.py
from pydantic import BaseModel, Field
from kimi_agent_sdk import CallableTool2, ToolOk, ToolError, ToolReturnValue
from typing import Literal


class UpdateContextParams(BaseModel):
    """上下文更新参数"""
    key: str = Field(description="上下文键名")
    value: dict = Field(description="要设置的值")
    operation: Literal["set", "append", "remove"] = Field(
        default="set",
        description="操作类型: set(设置), append(追加), remove(移除)"
    )


class UpdateContextTool(CallableTool2):
    """更新共享 subject_context"""
    name: str = "update_context"
    description: str = "更新共享执行上下文"
    params: type[UpdateContextParams] = UpdateContextParams

    def __init__(self, context_store):
        super().__init__()
        self._context_store = context_store

    async def __call__(self, params: UpdateContextParams) -> ToolReturnValue:
        try:
            self._context_store.update(
                key=params.key,
                value=params.value,
                operation=params.operation,
            )
            return ToolOk(output=f"Context '{params.key}' updated ({params.operation})")
        except Exception as exc:
            return ToolError(output="", message=str(exc), brief="Context update failed")
```

### 7.2 Agent File 配置

```yaml
# docuswarm/agents/configs/independent_agent.yaml
version: 1
agent:
  extend: default
  tools:
    - "docuswarm.tools.create_deliverable:CreateDeliverableTool"
    - "docuswarm.tools.update_context:UpdateContextTool"
```

### 7.3 工具注册流程对比

```
改造前:
  Agent 手动定义 JSON Schema → 传入 KimiClient.chat(tools=[...])
  Agent 手动解析 tool_calls → 手动执行工具 → 手动构造返回消息

改造后:
  CallableTool2 定义 → agent_file.yaml 注册 → SDK 自动调度
  SDK 接收 ToolCall → 自动反序列化参数（Pydantic） → 调用 __call__ → 自动返回 ToolResult
```

---

## 8. 会话管理改造

### 8.1 Session 持久化策略

```
改造后的会话管理:

Pipeline 级别:
  pipeline_session_id = f"docuswarm-{pipeline_id}"

节点级别:
  node_session_id = f"docuswarm-{pipeline_id}-{node_id}"

迭代级别（Independent Agent 多轮）:
  iteration_session_id = f"docuswarm-{pipeline_id}-{node_id}-iter{n}"
```

### 8.2 会话恢复与检查点集成

```python
# Pipeline 恢复流程
class PipelineOrchestrator:
    async def resume_pipeline(self, pipeline_id: str) -> None:
        """恢复中断的 Pipeline"""

        # 1. 从 SQLite 获取 Pipeline 状态
        pipeline_state = await self.state_manager.get_pipeline(pipeline_id)
        last_node = pipeline_state["current_node"]

        # 2. 尝试恢复 SDK Session
        session = await self.session_manager.resume_session(
            session_id=f"docuswarm-{pipeline_id}-{last_node}"
        )

        if session:
            # 3a. Session 存在 → 从上次中断处继续
            result = await self._continue_node(session, pipeline_state)
        else:
            # 3b. Session 不存在 → 重新创建
            result = await self._restart_node(pipeline_id, last_node)
```

### 8.3 Session 与 LangGraph Checkpoint 关系

```
LangGraph Checkpoint (SQLite):
  ├── 管理 Pipeline 全局状态 (PipelineState)
  ├── 管理节点间数据传递 (deliverables, questions, evaluations)
  └── 管理 DAG 执行进度

kimi-agent-sdk Session:
  ├── 管理 Agent 与 LLM 的对话历史
  ├── 管理工具调用上下文
  └── 管理迭代反馈状态

两者互补，不冲突:
  LangGraph → 宏观编排状态
  SDK Session → 微观对话状态
```

---

## 9. 取消机制改造

### 9.1 现有状态

docuswarm 核心层当前无原生取消支持，仅依赖 httpx 请求超时。

### 9.2 改造后取消机制

kimi-agent-sdk 提供原生取消能力：

```python
# Session 级别取消
session = await Session.create(...)

# 在另一个协程中取消
session.cancel()  # 设置内部 asyncio.Event

# prompt() 协程收到取消信号后抛出 RunCancelled
try:
    async for wire_msg in session.prompt(user_input):
        ...
except RunCancelled:
    logger.info("Agent execution cancelled")
```

**取消流程**:
```
外部请求取消
  → session.cancel()
    → asyncio.Event.set()
      → KimiCLI.run() 检测到 cancel_event
        → 抛出 RunCancelled 异常
          → async context manager 自动清理资源
```

### 9.3 Pipeline 级取消集成

```python
# docuswarm/pipeline/orchestrator.py
class PipelineOrchestrator:
    async def cancel_current_node(self, pipeline_id: str) -> None:
        """取消当前正在执行的节点"""
        session_id = self._get_current_session_id(pipeline_id)
        session = self.session_manager.get_active(session_id)
        if session:
            session.cancel()  # SDK 原生取消，单步操作
```

---

## 10. 审批与安全控制

### 10.1 审批策略设计

```python
# docuswarm/llm/approval.py
from kimi_agent_sdk import ApprovalRequest


class DocuSwarmApprovalHandler:
    """DocuSwarm 审批策略"""

    # 自动批准的操作列表（安全操作）
    AUTO_APPROVE_ACTIONS = {
        "create_deliverable",  # 创建文档
        "update_context",      # 更新上下文
        "read_file",           # 读取文件
    }

    # 需要拒绝的操作（文档编排场景不需要）
    REJECT_ACTIONS = {
        "write_file",          # 写文件
        "execute_command",     # 执行命令
        "delete_file",         # 删除文件
    }

    def __init__(self, auto_approve_all: bool = False):
        self._auto_approve_all = auto_approve_all

    def handle(self, request: ApprovalRequest) -> None:
        """审批处理回调"""
        if self._auto_approve_all:
            request.resolve("approve")
            return

        action = request.action
        if action in self.AUTO_APPROVE_ACTIONS:
            request.resolve("approve")
        elif action in self.REJECT_ACTIONS:
            request.resolve("reject")
        else:
            # 未知操作，批准单次（保守策略）
            request.resolve("approve")
```

### 10.2 上下文隔离与审批的关系

```
Independent Agent:
  → yolo=True (自动批准所有工具调用)
  → 原因: 工具仅为 create_deliverable 和 update_context，均为安全操作

Evaluator Agent:
  → 无工具调用 → 无需审批
  → 使用 prompt() 高级 API + thinking 模式
  → 上下文隔离保护（ContextFilter）保持不变
```

---

## 11. 风险评估与缓解

### 11.1 高风险

| 风险 | 影响 | 概率 | 缓解 |
|------|------|------|------|
| **kimi-cli 进程依赖** | SDK 通过 kimi-cli 子进程通信，非直接 HTTP | 高 | 确保 kimi-cli 安装正确，版本锁定 `>=1.12.0,<1.13.0` |
| **kosong 类型系统** | Message/ContentPart 等类型来自 kosong 包，与现有 ChatResponse 不兼容 | 中 | 创建适配层或全面替换为 SDK 类型 |
| **Wire 协议稳定性** | Wire 消息格式可能跨版本变化 | 中 | 锁定 SDK 版本，监控更新日志 |

### 11.2 中风险

| 风险 | 影响 | 概率 | 缓解 |
|------|------|------|------|
| **速率限制双层冲突** | SDK 内部限流 + 现有 TokenBucketRateLimiter 可能冲突 | 中 | 先保留外层限流，观察后决定 |
| **会话存储位置** | SDK Session 状态存储路径可能与项目结构冲突 | 低 | 配置 work_dir 隔离 |
| **测试覆盖** | 所有 LLM 调用测试需要适配 SDK 类型 | 中 | 分阶段迁移，保留旧测试至验证通过 |

### 11.3 低风险

| 风险 | 影响 | 概率 | 缓解 |
|------|------|------|------|
| **KaosPath 适配** | SDK 要求 KaosPath 而非 pathlib.Path | 低 | 添加转换辅助函数 |
| **Thinking 模式映射** | 现有三模式 → SDK 的 model+thinking | 低 | 创建映射枚举 |
| **日志系统差异** | SDK 可能有自己的日志系统 | 低 | 统一配置 structlog |
| **Python 版本** | SDK 要求 Python 3.12+，DocuSwarm 当前 3.14+ | 低 | 已满足 |

---

## 12. 实施路线图

### Phase 0: 准备

**步骤**:
1. 安装 kimi-agent-sdk 及其依赖（kimi-cli, kosong）
2. 验证 kimi-cli `--wire` 模式在项目环境中可用
3. 创建 SDK 集成测试验证基本连通性
4. 备份现有 `KimiClient` 相关代码

**验收标准**: `prompt("Hello", yolo=True)` 成功返回消息

### Phase 1: 核心层改造

**步骤**:
1. 创建 `KimiSessionManager` 适配层
2. 创建 `ModeMapper` (ChatMode → SDK 参数)
3. 改造 `BaseAgent`：注入 `KimiSessionManager`
4. 改造 `EvaluatorAgent`：使用 `prompt()` + thinking
5. 改造 `IndependentAgent`：使用 `Session` + 工具

**验收标准**: docuswarm 核心层可通过 SDK 完成单节点执行

### Phase 2: 工具迁移

**步骤**:
1. 实现 `CreateDeliverableTool(CallableTool2)`
2. 实现 `UpdateContextTool(CallableTool2)`
3. 创建 `agent_file.yaml` 工具注册
4. 验证工具自动调度正确性
5. 移除旧的 JSON Schema 定义

**验收标准**: Independent Agent 通过 SDK 自动调度工具

### Phase 3: 会话与取消

**步骤**:
1. 实现 Session 持久化策略（session_id 命名规范）
2. 实现 Session 恢复与 LangGraph Checkpoint 集成
3. 实现取消机制（`session.cancel()` 集成到 Pipeline）
4. 实现审批策略（`DocuSwarmApprovalHandler`）
5. 验证取消和恢复流程

**验收标准**: Pipeline 可中断后恢复，取消操作正常

### Phase 4: 清理与优化

**步骤**:
1. 移除 `KimiClient` 和相关代码（`client.py`）
2. 评估并决定 `TokenBucketRateLimiter` 去留
3. 评估并决定 `RetryHandler` 去留
4. 更新 `pyproject.toml` 依赖
5. 更新所有测试
6. 更新文档

**验收标准**: 无遗留的旧调用代码，所有测试通过

---

## 13. 附录

### 13.1 依赖变更

```toml
# pyproject.toml 变更

# 移除（如仅用于 KimiClient）
# httpx>=0.27.0

# 新增
kimi-agent-sdk = ">=0.0.5,<0.1.0"
# kimi-cli 和 kosong 作为传递依赖自动安装

# 保留
langgraph = ">=0.2.0"
langgraph-checkpoint-sqlite = "*"
pydantic = ">=2.0.0"
structlog = ">=24.0.0"
```

### 13.2 ChatMode 映射

```python
# docuswarm/llm/mode_mapper.py

from dataclasses import dataclass

@dataclass
class SDKModeParams:
    """SDK 模式参数"""
    model: str
    thinking: bool
    max_steps_per_turn: int | None

# ChatMode → SDKModeParams 映射
MODE_MAP = {
    "instant": SDKModeParams(
        model="kimi",
        thinking=False,
        max_steps_per_turn=5,
    ),
    "thinking": SDKModeParams(
        model="kimi",
        thinking=True,
        max_steps_per_turn=10,
    ),
    "agent": SDKModeParams(
        model="kimi",
        thinking=False,
        max_steps_per_turn=50,
    ),
}
```

### 13.3 异常映射

```python
# 现有异常 → kimi-agent-sdk 异常映射

# HTTP 429        → ChatProviderError (APIStatusError)
# HTTP timeout    → APITimeoutError
# HTTP 5xx        → ChatProviderError (APIStatusError)
# 连接错误        → APIConnectionError
# 空响应          → APIEmptyResponseError
# 取消（新增）    → RunCancelled
# 步骤超限（新增）→ MaxStepsReached
# 配置错误        → ConfigError
# 工具错误        → InvalidToolError
```

### 13.4 关键文件变更清单

| 操作 | 文件 | 说明 |
|------|------|------|
| **新增** | `docuswarm/llm/session_manager.py` | KimiSessionManager |
| **新增** | `docuswarm/llm/mode_mapper.py` | 模式映射 |
| **新增** | `docuswarm/llm/approval.py` | 审批策略 |
| **新增** | `docuswarm/tools/create_deliverable.py` | CallableTool2 工具 |
| **新增** | `docuswarm/tools/update_context.py` | CallableTool2 工具 |
| **新增** | `docuswarm/agents/configs/independent_agent.yaml` | Agent 工具配置 |
| **修改** | `docuswarm/agents/base.py` | 注入 SessionManager |
| **修改** | `docuswarm/agents/independent.py` | Session API 调用 |
| **修改** | `docuswarm/agents/evaluator.py` | prompt() API 调用 |
| **修改** | `pyproject.toml` | 依赖变更 |
| **移除** | `docuswarm/llm/client.py` | KimiClient (Phase 4) |
| **评估** | `docuswarm/llm/rate_limit.py` | 可能移除 |
| **评估** | `docuswarm/llm/retry.py` | 可能移除 |
| **不变** | `docuswarm/context/isolation.py` | 上下文隔离（业务层） |
| **不变** | `docuswarm/context/filter.py` | ContextFilter（业务层） |
| **不变** | `docuswarm/storage/*` | 状态持久化（LangGraph Checkpoint） |
| **不变** | `docuswarm/pipeline/*` | Pipeline 编排（LangGraph StateGraph） |
| **不变** | `docuswarm/nodes/*` | DualAgentNode 编排逻辑 |

---

## 14. 实施问题发现 (2026-02-23)

### 14.1 消息内容提取缺陷 (P0)

**问题位置**: `orchestrator.py:223-231`

**根因**: 直接赋值 `content = msg.content`，未处理 SDK 返回的 `list[ContentPart]` 类型。

**问题代码**:
```python
# 错误：假设 msg.content 是字符串
for msg in reversed(messages):
    if msg.role == "assistant" and msg.content:
        content = msg.content  # ← 类型错误
        break
```

**修复方案**: 使用 `Message.extract_text()` 方法

```python
for msg in reversed(messages):
    if msg.role == "assistant" and msg.content:
        if hasattr(msg, "extract_text"):
            content = msg.extract_text()
        else:
            content = str(msg.content) if msg.content else ""
        break
```

**参考**: [DocuSwarm消息内容提取失败问题深度分析.md](../../autoBMAD/docuswarm/docs/DocuSwarm消息内容提取失败问题深度分析.md)

### 14.2 SDK 配置问题 (P0)

**问题**: `~/.kimi/config.toml` 重复定义导致 TOML 解析错误

**错误日志**:
```
Invalid TOML: Key "kimi-for-coding" already exists. at line 16 col 0
```

**修复**: 删除重复的 `[models.kimi-for-coding]` 定义

**正确配置**:
```toml
default_model = "kimi-for-coding"

[models."kimi-for-coding"]
provider = "managed:kimi-code"
model = "kimi-for-coding"
max_context_size = 262144
capabilities = ["image_in", "video_in", "thinking"]
```

**参考**: 
- [Kimi-K2.5-API-Error-Analysis-Report.md](../../autoBMAD/docuswarm/docs/Kimi-K2.5-API-Error-Analysis-Report.md)
- [Empty-Response-from-LLM-深度分析报告.md](../../autoBMAD/docuswarm/docs/Empty-Response-from-LLM-深度分析报告.md)

### 14.3 配置值对照表

| 配置项 | 错误值 | 正确值 |
|--------|--------|--------|
| `base_url` | `https://api.kimi.com/coding/` | `https://api.kimi.com/coding/v1` |
| `model` | `kimi-k2.5` | `kimi-for-coding` |
| `max_context_size` | `128000` | `262144` |

### 14.4 需修改文件清单 (追加)

| 文件 | 修改内容 | 优先级 |
|------|----------|--------|
| `orchestrator.py:223-231` | 使用 `extract_text()` | P0 |
| `~/.kimi/config.toml` | 删除重复定义 | P0 |
| `session_manager.py:100` | 修正 `base_url` 默认值 | P1 |
| `config.py:18,28-41` | 修正模型名称 | P1 |

---

**报告完成**

**更新日志**:
- 2026-02-20: 初始版本
- 2026-02-23: 添加第14章 - 实施问题发现

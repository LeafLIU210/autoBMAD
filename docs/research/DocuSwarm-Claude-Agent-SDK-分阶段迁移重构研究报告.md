# DocuSwarm Claude Agent SDK 分阶段迁移重构研究报告

## 文档信息

| 字段 | 内容 |
|---|---|
| 主题 | 基于 `epic_automation` 架构模式的 `claude-agent-sdk` 分阶段迁移方案 |
| 报告日期 | 2026-03-08 |
| 评估范围 | `@autoBMAD/docuswarm` 全量 AI SDK 迁移 |
| 明确前提 | 拒绝继续采用 Kimi API，采用 `epic_automation` 成熟架构模式 |
| 输出性质 | 架构重构研究报告 + 调试工具 + 迁移路线图 |

---

## 一、执行摘要

### 1.1 核心结论

**战略上必须迁移，工程上必须分阶段，架构上必须参考 `epic_automation`。**

当前 `autoBMAD/docuswarm` 的 AI 执行链路深度耦合 Kimi SDK，存在以下系统性问题：

1. **会话目录脆弱性**：Kimi SDK 默认会话目录落在用户目录下，存在写权限依赖
2. **连接稳定性问题**：存在多层串联故障（权限错误 → 连接失败 → 假成功）
3. **失败语义混乱**：节点失败后流水线仍可能被标记为 completed
4. **Provider 耦合**：配置、运行时、业务三层全部围绕 Kimi 构建

### 1.2 迁移策略

| 维度 | 策略 |
|---|---|
| 实施方式 | 分层适配 + 分阶段迁移 + 最后移除 Kimi 代码 |
| 参考架构 | `autoBMAD/epic_automation` 的 SDKExecutor + CancellationManager + SDKResult |
| 迁移顺序 | Phase 0 抽象层 → Phase 1 轻量调用 → Phase 2 IndependentAgent → Phase 3 编排链路 → Phase 4 移除 Kimi |
| 风险控制 | 每阶段独立测试通过后才进入下一阶段 |

---

## 二、当前架构深度分析

### 2.1 架构现状图谱

```
┌─────────────────────────────────────────────────────────────────┐
│                     DocuSwarm 当前架构                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Config     │───▶│KimiSession   │───▶│  Kimi SDK    │      │
│  │  (KIMI_*)    │    │  Manager     │    │ kimi-agent-  │      │
│  └──────────────┘    └──────────────┘    │    sdk       │      │
│         │                   │            └──────────────┘      │
│         │                   │                                    │
│         ▼                   ▼                                    │
│  ┌──────────────┐    ┌──────────────┐                          │
│  │   Agents     │◀───│   Session    │                          │
│  │ Independent  │    │ create/resume│                          │
│  │  Evaluator   │    │ single_prompt│                          │
│  └──────────────┘    └──────────────┘                          │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  DualAgent   │───▶│ Orchestrator │───▶│  LangGraph   │      │
│  │    Node      │    │ resume/restart    │  Checkpoints │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Kimi 语义渗透分析

#### 2.2.1 配置层依赖

```python
# autoBMAD/docuswarm/config.py
api_key = os.environ.get("KIMI_API_KEY")  # 硬编码 Kimi
base_url = os.environ.get("KIMI_BASE_URL", "https://api.kimi.com/coding/")
```

**问题**：`.env` 文件使用 `override=True`，即使系统环境设置 `ANTHROPIC_*` 也会被覆盖。

#### 2.2.2 运行时依赖

```python
# autoBMAD/docuswarm/llm/session_manager.py
from kimi_agent_sdk import (
    ApprovalHandlerFn,
    ChatProviderError,
    Config,
    ConfigError,
    InvalidToolError,
    MaxStepsReached,
    Message,
    RunCancelled,
    Session,
    WireMessage,
)
```

**关键耦合点**：
- `KimiSessionManager` 直接返回 `kimi_agent_sdk.Session`
- 使用 `kimi_agent_sdk.Message` 类型贯穿业务层
- `ApprovalRequest` 处理逻辑绑定 Kimi SDK 语义

#### 2.2.3 业务层依赖

```python
# autoBMAD/docuswarm/agents/independent.py
async for wire_msg in session.prompt(full_prompt):
    if isinstance(wire_msg, ApprovalRequest):  # Kimi 特有类型
        wire_msg.resolve("approve")
```

```python
# autoBMAD/docuswarm/agents/evaluator.py
sdk_response: list[Message] = await self.session_manager.single_prompt(
    prompt=full_prompt,
    mode="thinking",  # Kimi 特有模式
    yolo=True,
)
```

### 2.3 当前问题根因分析

| 问题现象 | 技术根因 | 架构根因 |
|---|---|---|
| 会话目录权限错误 | Kimi SDK 默认使用 `~/.kimi/sessions` | 没有接管会话持久化路径 |
| 连接失败不友好 | 异常直接透传到业务层 | 没有统一错误分类和映射层 |
| 假成功问题 | 失败节点状态被错误合并 | 缺乏 SDKResult 统一语义 |
| 恢复不可靠 | 旧会话/消息残留 | 没有 CancellationManager 清理确认 |

---

## 三、目标架构设计

### 3.1 目标状态架构

```
┌──────────────────────────────────────────────────────────────────────┐
│                   DocuSwarm 目标架构 (Post-Migration)                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│   │   Config     │───▶│  LLMRuntime  │───▶│  Claude Runtime      │  │
│   │ (ANTHROPIC_*)│    │  (Abstract)  │    │  (Implementation)    │  │
│   └──────────────┘    └──────────────┘    └──────────────────────┘  │
│          │                   │                    │                  │
│          │                   │                    ▼                  │
│          │                   │           ┌──────────────┐           │
│          │                   │           │ SDKExecutor  │           │
│          │                   │           │   +          │           │
│          │                   │           │ Cancellation │           │
│          │                   │           │   Manager    │           │
│          │                   │           └──────────────┘           │
│          ▼                   ▼                    │                  │
│   ┌──────────────┐    ┌──────────────┐          │                   │
│   │   Agents     │◀───│  sdk_helper  │◀─────────┘                   │
│   │ Independent  │    │ (Narrow API) │                               │
│   │  Evaluator   │    └──────────────┘                               │
│   └──────────────┘                                                   │
│          │                                                            │
│          ▼                                                            │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│   │  DualAgent   │───▶│ Orchestrator │───▶│  LangGraph   │          │
│   │    Node      │    │ resume/restart    │  Checkpoints │          │
│   └──────────────┘    │   (Confirmed)     │  (Confirmed) │          │
│                       └──────────────┘    └──────────────┘          │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.2 核心组件设计

#### 3.2.1 SDKResult（移植自 epic_automation）

```python
@dataclass
class SDKResult:
    # 业务成功标志
    has_target_result: bool = False
    cleanup_completed: bool = False
    
    # 执行信息
    duration_seconds: float = 0.0
    session_id: str = ""
    agent_name: str = ""
    
    # 结果数据
    messages: list[Any] = field(default_factory=list)
    target_message: Any = None
    
    # 错误分类
    error_type: SDKErrorType = SDKErrorType.SUCCESS
    errors: list[str] = field(default_factory=list)
    
    def is_success(self) -> bool:
        return self.has_target_result and self.cleanup_completed
```

**价值**：
- 显式区分"业务成功"与"底层异常"
- 统一错误分类（SUCCESS/CANCELLED/TIMEOUT/SDK_ERROR/UNKNOWN）
- 避免"节点失败但流程成功"的语义混乱

#### 3.2.2 CancellationManager（移植自 epic_automation）

```python
class CancellationManager:
    """双条件验证机制的取消管理器"""
    
    async def confirm_safe_to_proceed(self, call_id: str, timeout: float = 30.0) -> bool:
        """确认可以安全进行下一步
        
        条件：cancel_requested=True AND cleanup_completed=True
        """
```

**价值**：
- resume/restart 前确认资源已清理
- 防止旧会话、旧任务残留影响后续节点
- 提供可靠的运行时边界

#### 3.2.3 SDKExecutor（移植自 epic_automation）

```python
class SDKExecutor:
    async def execute(
        self,
        sdk_func: Callable[[], AsyncIterator[Any]],
        target_predicate: Callable[[Any], bool],
        *,
        timeout: float | None = None,
        agent_name: str = "Unknown"
    ) -> SDKResult:
        """在独立TaskGroup中执行SDK调用"""
```

**价值**：
- 隔离 Provider 连接异常与业务失败
- 统一超时、取消、异常映射
- 业务层无需直接关心 SDK 底层细节

### 3.3 运行时抽象层设计

#### 3.3.1 抽象接口（新增）

```python
# autoBMAD/docuswarm/llm/runtime.py

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator

class LLMRuntime(ABC):
    """Provider-neutral LLM runtime interface"""
    
    @abstractmethod
    async def execute_prompt(
        self,
        prompt: str,
        *,
        mode: str = "agent",
        auto_approve: bool = True,
        timeout: float | None = None,
    ) -> SDKResult:
        """Execute a single prompt and return standardized result"""
    
    @abstractmethod
    async def create_session(
        self,
        work_dir: Path,
        agent_file: Path | None = None,
    ) -> str:
        """Create a new session, return session_id"""
    
    @abstractmethod
    async def resume_session(self, session_id: str) -> bool:
        """Resume an existing session"""
    
    @abstractmethod
    async def cancel_execution(self, session_id: str) -> bool:
        """Cancel ongoing execution with cleanup confirmation"""
```

#### 3.3.2 Claude 实现（新增）

```python
# autoBMAD/docuswarm/llm/claude_runtime.py

class ClaudeRuntime(LLMRuntime):
    """Claude Agent SDK runtime implementation"""
    
    def __init__(self):
        self._executor = SDKExecutor()
        self._cancel_manager = CancellationManager()
```

---

## 四、迁移阶段详细规划

### Phase 0：运行时抽象层建设

**目标**：建立 provider-neutral 抽象，让业务层不再直接依赖 Kimi 类型

**新增文件**：
```
autoBMAD/docuswarm/llm/
├── runtime.py              # LLMRuntime 抽象接口
├── claude_runtime.py       # ClaudeRuntime 实现
├── sdk_result.py           # SDKResult + SDKErrorType
├── cancellation_manager.py # CancellationManager
└── sdk_executor.py         # SDKExecutor

autoBMAD/docuswarm/agents/
└── sdk_helper.py           # execute_sdk_call 统一入口
```

**修改文件**：
```
autoBMAD/docuswarm/config.py
# 添加 ANTHROPIC_API_KEY 支持，保持 KIMI_API_KEY 向后兼容
# 详见 P1-2 测试驱动方案: docs/solution/2026-04-03-p1-2-config-semantics-test-driven-plan.md
```

> **P1-2 配置语义统一**: 配置命名迁移遵循测试驱动方案，分 5 个 Phase 实施：
> - Phase 1: `config.py` 支持 `ANTHROPIC_*`，`KIMI_*` 兼容 deprecation 警告
> - Phase 2: `session_manager.py` 移除未消费字段，清理 `CLAUDE_*`
> - Phase 3: `dual_agent.py` 使用统一 `Config`
> - Phase 4: 文档统一
> - Phase 5: 移除兼容层

**验收标准**:
- [ ] 新组件单元测试通过率 100%
- [ ] 不破坏现有 Kimi 代码路径
- [ ] Context Validator 可用新运行时正常工作

### Phase 1：轻量调用路径迁移

**目标对象**：
1. Context Validator（`orchestrator._validate_context()`）
2. EvaluatorAgent（主要通过 `single_prompt()` 工作）

**迁移内容**：
```python
# 修改前 (Kimi)
messages: list[Message] = await session_manager.single_prompt(
    prompt=prompt,
    mode="thinking",
    yolo=True,
)

# 修改后 (Claude Runtime)
result: SDKResult = await sdk_helper.execute_sdk_call(
    prompt=prompt,
    agent_name="ContextValidator",
    timeout=60.0,
)
if result.is_success():
    content = extract_result_content(result.target_message)
```

**验收标准**：
- [ ] Context Validation 正常工作
- [ ] EvaluatorAgent 评分准确
- [ ] 性能不低于 Kimi 版本

### Phase 2：IndependentAgent 迁移

**目标**：迁移最复杂的工具调用链路

**关键改动**：
1. **工具注册**：从 Kimi `agent_file` 切换到 Claude 工具注册
2. **审批策略**：从 Kimi `ApprovalRequest` 切换到 provider-neutral 策略
3. **消息解析**：适配 Claude 消息格式

```python
# 新增审批策略层
# autoBMAD/docuswarm/llm/approval_policy.py

@dataclass
class ToolApprovalPolicy:
    auto_approve_tools: set[str]
    reject_tools: set[str]
    default_policy: Literal["approve", "reject", "prompt"]
    
    def should_approve(self, tool_name: str) -> bool:
        ...
```

**验收标准**：
- [ ] `create_deliverable` 工具正常触发
- [ ] 交付物正确写入文件
- [ ] 迭代循环正常工作

### Phase 3：编排恢复链路迁移

**目标**：迁移 `resume/restart/cancel` 与状态机语义

**关键改动**：
1. **取消确认**：采用显式 `confirm_safe_to_proceed()`
2. **状态语义**：重新定义"失败/可恢复/已完成"
3. **清理保证**：resume 前确认上一个执行上下文已终结

```python
# 修改前 (Kimi)
session = await session_manager.resume_session(session_id)

# 修改后 (Claude Runtime)
# 1. 先确认上一个调用已清理
await cancellation_manager.confirm_safe_to_proceed(last_call_id)
# 2. 再恢复或创建新会话
success = await runtime.resume_session(session_id)
```

**验收标准**：
- [ ] `cancel` 后资源完全清理
- [ ] `resume` 能正确恢复或重建
- [ ] `restart` 清除后续节点状态

### Phase 4：Kimi 代码移除

**移除内容**：
```
autoBMAD/docuswarm/llm/
├── session_manager.py      # KimiSessionManager
└── approval.py             # Kimi 专属审批逻辑

# 配置清理
autoBMAD/docuswarm/config.py
# 移除 KIMI_* 配置
```

**文档更新**：
- 更新 README.md
- 更新 CONFIGURATION.md
- 更新所有环境变量说明

---

## 五、风险分析与缓解策略

### 5.1 高风险项

| 风险 | 影响 | 概率 | 缓解策略 |
|---|---|---|---|
| 工具调用机制不兼容 | IndependentAgent 无法创建交付物 | 中 | Phase 2 开始前做 POC 验证 |
| 消息格式差异导致解析失败 | Evaluator 无法评分 | 低 | Phase 1 包含完整测试覆盖 |
| Cancel Scope 跨任务错误 | 恢复/取消不可靠 | 中 | 复用 epic_automation 已验证方案 |
| 新旧语义混杂 | 技术债加倍 | 高 | 严格执行阶段隔离，每阶段完全通过才进入下一阶段 |

### 5.2 回滚策略

每个 Phase 必须保持：
1. **Git Tag**：每阶段完成打标签
2. **Feature Flag**：运行时切换 Kimi/Claude（仅用于开发/测试）
3. **数据库兼容**：状态结构保持兼容或提供迁移脚本

---

## 六、工作量估算

| Phase | 文件变更 | 新增文件 | 估算工时 | 依赖 |
|---|---|---|---|---|
| Phase 0 | 2 | 6 | 3-4 天 | 无 |
| Phase 1 | 4 | 1 | 2-3 天 | Phase 0 |
| Phase 2 | 6 | 2 | 4-5 天 | Phase 1 |
| Phase 3 | 4 | 0 | 2-3 天 | Phase 2 |
| Phase 4 | 6 | 0 | 1-2 天 | Phase 3 |
| **总计** | **22** | **9** | **12-17 天** | - |

---

## 七、附录

### 7.1 关键文件映射

| 功能 | 当前 (Kimi) | 目标 (Claude) |
|---|---|---|
| Session 管理 | `llm/session_manager.py` | `llm/claude_runtime.py` |
| 审批处理 | `llm/approval.py` | `llm/approval_policy.py` |
| 错误分类 | 无统一分类 | `llm/sdk_result.py` |
| 取消管理 | 无 | `llm/cancellation_manager.py` |
| Agent 统一入口 | 各 Agent 直接调用 | `agents/sdk_helper.py` |

### 7.2 测试策略

每个 Phase 必须包含：
1. **单元测试**：新组件独立测试
2. **集成测试**：与现有编排层集成
3. **端到端测试**：完整 pipeline 执行
4. **故障注入测试**：模拟取消、超时、网络失败

### 7.3 参考资源

- `autoBMAD/epic_automation/core/sdk_result.py`
- `autoBMAD/epic_automation/core/cancellation_manager.py`
- `autoBMAD/epic_automation/core/sdk_executor.py`
- `autoBMAD/epic_automation/agents/sdk_helper.py`
- `autoBMAD/epic_automation/sdk_wrapper.py`

---

## 八、结论与建议

### 8.1 最终建议

**推荐方案：基于 `epic_automation` 架构模式的 `claude-agent-sdk` 分阶段迁移方案**

战略上应淘汰 Kimi，战术上应渐进替换：

1. **立即开始 Phase 0**：建立运行时抽象层，不碰业务行为
2. **优先迁移 EvaluatorAgent**：单轮 prompt，风险最低，可快速验证
3. **谨慎处理 IndependentAgent**：工具调用链路最复杂，需要充分测试
4. **彻底修复状态语义**：即使迁移完成，也要解决"假成功"问题

### 8.2 不推荐方案

| 方案 | 原因 |
|---|---|
| 继续围绕 Kimi 修补 | 长期收益有限，技术债持续累积 |
| 直接替换所有 Kimi 调用 | 风险过高，没有中间抽象层保护 |
| 保留 Kimi 兼容层长期共存 | 新旧语义混杂，维护成本加倍 |

### 8.3 Go / No-Go 决策

| 检查项 | 状态 |
|---|---|
| epic_automation 架构已验证 | ✓ 已稳定运行 |
| claude-agent-sdk 可用 | ✓ 已在 epic_automation 中使用 |
| 团队熟悉 epic_automation | △ 需要知识传递 |
| 测试覆盖率充足 | ✗ 需要补充 |
| 回滚策略就绪 | △ 需要完善 |

**建议**：在满足"测试覆盖率"和"回滚策略"条件后，正式启动 Phase 0。

---

*报告完成*

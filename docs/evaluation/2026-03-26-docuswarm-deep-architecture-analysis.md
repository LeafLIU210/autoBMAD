# DocuSwarm 深度架构分析报告

**日期**: 2026-03-26  
**分析类型**: 架构设计评估与优化建议  
**分析范围**: autoBMAD.docuswarm 核心架构  

---

## 目录

1. [Context Validator 提取重构的必要性](#1-context-validator-提取重构的必要性)
2. [MemoryManager 的意义评估](#2-memorymanager-的意义评估)
3. [Task 任务契约的存废分析](#3-task-任务契约的存废分析)
4. [节点 Agent 文档读取能力评估](#4-节点-agent-文档读取能力评估)
5. [Evaluator Agent 上下文选择](#5-evaluator-agent-上下文选择)

---

## 1. Context Validator 提取重构的必要性

### 1.1 当前实现的问题

**代码位置**: `orchestrator.py` 第262-345行 (约80行)

```python
async def _validate_context(self, subject_context: dict[str, Any]) -> dict[str, Any]:
    """Validate subject context using LLM (Kimi Instant)."""
    logger.info("validating_context", context=subject_context)
    
    # 1. 直接内联在 Orchestrator 中
    # 2. 使用 try-except 包裹的 fail-open 策略
    # 3. JSON 解析失败时返回默认值
    try:
        # ... validation logic ...
    except Exception as e:
        # Fail open - allow pipeline to proceed if LLM is unavailable
        return {
            "valid": True,
            "reason": f"LLM validation failed: {e}, defaulting to valid",
            "missing_info": [],
        }
```

### 1.2 违反的设计原则

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    单一职责原则 (SRP) 违反                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  HybridOrchestrator 当前职责：                                               │
│  ├─ 流程控制 (start_pipeline, resume_pipeline)                              │
│  ├─ 状态管理 (checkpoint, state persistence)                                │
│  ├─ 会话管理 (session resume, cancellation)                                 │
│  ├─ 依赖检查 (_check_dependencies)                                          │
│  ├─ 上下文验证 (_validate_context) ← 不应该在这里！                          │
│  └─ 异常处理 (escalation, force completion)                                 │
│                                                                             │
│  问题：一个类承担了太多职责，导致：                                           │
│  1. 测试困难 - 验证逻辑与流程控制耦合                                         │
│  2. 复用受阻 - 其他组件无法独立使用验证功能                                    │
│  3. 维护成本 - 修改验证逻辑可能影响流程控制                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 提取重构的必要性

#### 1.3.1 职责分离

```
重构前：
┌─────────────────────────────────────┐
│      HybridOrchestrator             │
│  ┌─────────────────────────────┐   │
│  │   _validate_context()       │   │ ← 内联80行
│  │   - Prompt构建              │   │
│  │   - LLM调用                 │   │
│  │   - JSON解析                │   │
│  │   - 重试逻辑                │   │
│  │   - 失败处理                │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │   start_pipeline()          │   │ ← 调用验证
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘

重构后：
┌─────────────────────┐    ┌──────────────────────────────┐
│ HybridOrchestrator  │    │    ContextValidator          │
│                     │    │  ┌────────────────────────┐  │
│  start_pipeline() ──┼───►│  │ validate()             │  │
│                     │    │  │ - Prompt构建            │  │
│  _get_validator()   │    │  │ - LLM调用               │  │
│                     │    │  │ - JSON解析              │  │
└─────────────────────┘    │  │ - 结构化重试            │  │
                           │  │ - 策略处理              │  │
                           │  └────────────────────────┘  │
                           └──────────────────────────────┘
```

#### 1.3.2 可配置性与策略化

**当前**: fail-open 硬编码，无法根据环境调整

```python
# 当前：无法配置
except Exception as e:
    return {"valid": True, ...}  # 永远 fail-open
```

**重构后**: 支持策略配置

```python
class ContextValidator:
    def __init__(self, fail_open: bool = False, max_retries: int = 2):
        self._fail_open = fail_open  # 可配置！
        self._max_retries = max_retries
    
    async def _handle_failure(self, ...):
        if self._fail_open:
            return ValidationResult(valid=True, fallback_used=True)
        else:
            raise ContextValidationError(...)  # 严格模式
```

#### 1.3.3 可观测性提升

| 指标 | 当前 | 重构后 |
|------|------|--------|
| 重试次数 | 不可见 | `ValidationResult.attempts` |
| Fallback使用 | 日志警告 | `ValidationResult.fallback_used` |
| 原始响应 | 丢失 | `ValidationResult.raw_response` |
| 失败原因 | 简化 | 结构化 `missing_info` |

### 1.4 重构实施建议

**分阶段实施**：

```
Phase 1: 创建 ContextValidator 组件
├── 创建 pipeline/context_validator.py
├── 实现 ValidationResult 数据类
└── 实现基础验证逻辑 (US-13.1~13.3)

Phase 2: 增强与策略
├── 实现结构化重试 (US-13.4)
└── 实现 fail-open/close 策略 (US-13.5)

Phase 3: 集成与迁移
├── Orchestrator 集成 (US-13.6)
├── 添加配置项 (env var, config file)
└── 移除旧代码

Phase 4: 测试与监控
├── 单元测试覆盖 >= 90%
├── 集成测试
└── 监控 dashboard
```

---

## 2. MemoryManager 的意义评估

### 2.1 MemoryManager 设计意图

**代码位置**: `context/memory.py`

```python
class MemoryScope(Enum):
    SHARED = "shared"       # 两个 Agent 都可访问
    INDEPENDENT = "independent"  # 仅 Independent Agent
    EVALUATOR = "evaluator"      # 仅 Evaluator Agent

class MemoryManager:
    """三层内存隔离架构"""
    def __init__(self):
        self._shared_memory: dict[str, Any] = {}
        self._independent_memory: dict[str, Any] = {}
        self._evaluator_memory: dict[str, Any] = {}
```

### 2.2 当前架构中的位置

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    当前状态：MemoryManager 已实现但未启用                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DualAgentNode.__init__ (dual_agent.py)                                     │
│  ├── self.context_manager = ContextManager()          ✅ 已启用             │
│  ├── self.context_filter = ContextFilter()            ✅ 已启用             │
│  ├── self.audit_logger = IsolationAuditLogger()       ✅ 已启用             │
│  └── self.memory_manager = ???                        ❌ 未传入/未使用      │
│                                                                             │
│  问题：                                                                      │
│  1. MemoryManager 实例在 DualAgentNode 中不存在                              │
│  2. 当前使用 PipelineState.shared_context 传递共享状态                      │
│  3. 缺少内存级别的隔离机制                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 意义评估：是否需要 MemoryManager？

#### 2.3.1 支持保留 MemoryManager 的观点

| 价值点 | 说明 |
|--------|------|
| **内存级隔离** | 比字典更严格的访问控制，防止意外泄露 |
| **作用域清晰** | 显式区分 SHARED/INDEPENDENT/EVALUATOR |
| **审计友好** | 所有读写操作可统一日志记录 |
| **未来扩展** | 支持持久化、分布式内存等高级特性 |

#### 2.3.2 反对保留的观点（奥卡姆剃刀）

| 论点 | 说明 |
|------|------|
| **当前已够用** | PipelineState.shared_context 已能满足跨节点共享 |
| **复杂度增加** | 三层内存模型增加理解和维护成本 |
| **功能重叠** | ContextManager 已处理大部分隔离需求 |
| **无实际需求** | 当前没有 Evaluator 需要私有内存的用例 |

### 2.4 深度分析：MemoryManager vs shared_context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    两种架构对比                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  架构 A：当前实现 (shared_context)                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PipelineState.shared_context                                       │   │
│  │  ├── facts.*                    ← Independent 写入                  │   │
│  │  ├── decisions.*                ← Independent 写入                  │   │
│  │  └── notes                      ← Independent 写入                  │   │
│  │                                                                     │   │
│  │  访问控制：通过 update_context tool 的白名单机制                       │   │
│  │  隔离级别：逻辑隔离（约定优于配置）                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  架构 B：设计实现 (MemoryManager)                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  MemoryManager                                                      │   │
│  │  ├── _shared_memory             ← 双方读写                          │   │
│  │  ├── _independent_memory        ← 仅 Independent                    │   │
│  │  └── _evaluator_memory          ← 仅 Evaluator                      │   │
│  │                                                                     │   │
│  │  访问控制：通过 API 强制隔离                                          │   │
│  │  隔离级别：物理隔离（运行时强制）                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.5 建议：延迟启用 MemoryManager

```
决策：暂不集成 MemoryManager，但保留代码

理由：
1. 当前 shared_context + ContextManager 已满足 P0-1 单一上下文协议
2. 没有明确的 Evaluator 私有内存需求
3. 增加复杂度却无即时收益，违反奥卡姆剃刀原则
4. 未来如需更严格的内存隔离，可随时启用

行动项：
- 保留 memory.py 代码
- 添加文档说明："预留用于未来严格内存隔离需求"
- 在 DualAgentNode 中注释说明未使用原因
```

---

## 3. Task 任务契约的存废分析

### 3.1 当前 Task 契约定义

**node.yaml 示例** (analyst/node.yaml):
```yaml
task:
  name: create-product-brief
  description: "Create a comprehensive product brief..."
  role_supplement: "As a Business Analyst, focus on..."
```

**NodeExecutionContext 中的映射**:
```python
# context_builder.py 第61-64行
task_name=node_config.task.get("name", node_config.name),
task_description=node_config.description or node_config.task.get("description", ""),
role_supplement=node_config.task.get("role_supplement", ""),
```

### 3.2 奥卡姆剃刀分析

#### 3.2.1 如无必要，勿增实体

```
当前实体：
┌─────────────────────────────────────────────────────────────┐
│ 实体列表                                                     │
├─────────────────────────────────────────────────────────────┤
│ 1. node_id      - 节点唯一标识                               │
│ 2. node_name    - 节点显示名称                               │
│ 3. task_name    - 任务名称                                   │
│ 4. task_description - 任务描述                               │
│ 5. role_supplement  - 角色补充                               │
│ 6. persona.*    - 角色身份定义 (persona.json)                │
├─────────────────────────────────────────────────────────────┤
│ 问题：                                                       │
│ - task_name 与 node_name 是否重复？                          │
│ - task_description 与 persona.identity 是否重复？            │
│ - role_supplement 与 persona.role 是否重复？                 │
└─────────────────────────────────────────────────────────────┘
```

#### 3.2.2 实际使用分析

| 字段 | 当前值示例 | 替代方案 | 是否可移除 |
|------|-----------|----------|-----------|
| `task_name` | "create-product-brief" | 使用 `node_id` 或 `node_name` | ✅ 可移除 |
| `task_description` | "Create a comprehensive product brief..." | 使用 `persona.identity` | ⚠️ 需评估 |
| `role_supplement` | "As a Business Analyst..." | 使用 `persona.role` + 节点类型推导 | ✅ 可移除 |

### 3.3 节点单一职责论证

**核心观点**：每个节点应该只执行一个明确的任务，task 契约是冗余的。

```
节点职责矩阵：

┌─────────────┬─────────────────────────────┬─────────────────────────────┐
│   节点      │       职责 (单一)            │        Task 契约冗余度       │
├─────────────┼─────────────────────────────┼─────────────────────────────┤
│ analyst     │ 分析需求，产出 Product Brief │ task_name: create-product-   │
│             │                             │ brief → 与节点职责完全相同   │
├─────────────┼─────────────────────────────┼─────────────────────────────┤
│ pm          │ 定义产品需求，产出 PRD        │ task_name: create-prd →      │
│             │                             │ 与节点职责完全相同           │
├─────────────┼─────────────────────────────┼─────────────────────────────┤
│ ux          │ 设计用户体验                  │ task_name: create-ux-design  │
│             │                             │ → 与节点职责完全相同         │
├─────────────┼─────────────────────────────┼─────────────────────────────┤
│ architect   │ 设计系统架构                  │ task_name: create-arch-doc   │
│             │                             │ → 与节点职责完全相同         │
├─────────────┼─────────────────────────────┼─────────────────────────────┤
│ po          │ 拆分用户故事                  │ task_name: create-epics-     │
│             │                             │ stories → 与节点职责相同     │
└─────────────┴─────────────────────────────┴─────────────────────────────┘
```

### 3.4 优化方案：移除 Task 契约

#### 3.4.1 简化后的 NodeExecutionContext

```python
# 当前（复杂）
class NodeExecutionContext(NodeExecutionContextRequired, total=False):
    # === 任务契约 ===  ← 移除这一组
    task_name: str
    task_description: str
    role_supplement: str
    
    # === 交付物契约 ===
    deliverable_type: str
    deliverable_requirements: DeliverableRequirements
    
    # === 上下文数据 ===
    original_context: dict[str, Any]
    chained_deliverables: list[dict[str, Any]]
    shared_context: dict[str, Any]

# 简化后
class NodeExecutionContext(NodeExecutionContextRequired, total=False):
    # === 身份标识 ===  ← 保留
    pipeline_id: str
    node_id: str
    node_name: str
    node_order: int
    
    # === 交付物契约 ===  ← 保留
    deliverable_type: str
    deliverable_requirements: DeliverableRequirements
    
    # === 上下文数据 ===  ← 保留
    original_context: dict[str, Any]
    chained_deliverables: list[dict[str, Any]]
    shared_context: dict[str, Any]
    
    # persona 通过 node_id 动态加载，不存于 context
```

#### 3.4.2 职责推导逻辑

```python
# contract_builder.py 简化

class NodePromptContractBuilder:
    def _build_task_section(self, context: NodeExecutionContext) -> str:
        """从 node_id 推导任务描述，无需 task 契约"""
        node_id = context["node_id"]
        node_name = context["node_name"]
        
        # 职责映射表（单一职责）
        NODE_PURPOSE = {
            "analyst": "分析业务需求，产出 Product Brief",
            "pm": "定义产品需求，产出 PRD",
            "ux": "设计用户体验，产出 UX Design",
            "architect": "设计系统架构，产出 Architecture Document",
            "po": "拆分用户故事，产出 Epics 和 Stories",
        }
        
        purpose = NODE_PURPOSE.get(node_id, "执行节点任务")
        
        return f"""## 任务

你正在执行 **{node_name}** 节点的职责。

{purpose}
"""
    
    def _build_persona_section(self, context: NodeExecutionContext) -> str:
        """从 persona.json 加载，无需 role_supplement"""
        node_id = context["node_id"]
        persona = PersonaLoader.load(node_id)
        return PersonaLoader.format_system_prompt(persona)
```

### 3.5 实施建议

```
决策：移除 Task 契约，简化架构

实施步骤：
1. 更新 node.yaml - 移除 task 部分
2. 更新 NodeConfig - 移除 task 字段
3. 更新 context_builder.py - 移除 task 相关字段构建
4. 更新 contracts.py - 从 NodeExecutionContext 移除 task 字段
5. 更新 contract_builder.py - 使用 node_id 推导任务描述
6. 测试所有节点确保行为一致

收益：
- 减少配置复杂度
- 消除重复信息 (DRY)
- 强化单一职责原则
- 降低认知负担
```

---

## 4. 节点 Agent 文档读取能力评估

### 4.1 问题拆解

核心问题：
1. Claude Agent SDK 是否具备读取引用文档的能力？
2. 节点职责契约（persona）应如何注入？
3. 是否应优化契约让 Agent 主动读取引用文档？

### 4.2 Claude Agent SDK 能力分析

#### 4.2.1 工具集限制的架构设计原理

Claude Agent SDK 的工具集限制并非技术缺陷，而是基于 Anthropic **"显式边界优于意图"**（Explicit Boundaries Over Intentions）的核心安全哲学。根据 Anthropic 官方设计原则与工程实践，工具集限制存在以下深层原因：

**1. 安全边界与权限最小化原则**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Anthropic 安全设计三层模型                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Layer 1: 环境硬化 (Environment Hardening)                                  │
│  ├── 隔离执行环境 (Sandbox)                                                  │
│  ├── 受限的凭证访问 ("Remove credentials, inject agent identities")          │
│  └── 域名白名单替代全网访问 (Allowlist domains)                               │
│                                                                             │
│  Layer 2: 工具级显式授权 (Explicit Tool Authorization)                       │
│  ├── 默认只读权限 (Out-of-box read-only)                                     │
│  ├── 写入操作需人工批准 (Human-in-the-loop for edits)                        │
│  └── 工具集白名单定义能力边界 (Tool allowlist defines capability boundary)    │
│                                                                             │
│  Layer 3: 运行时验证 (Runtime Verification)                                  │
│  ├── 结构化检查清单 (Structured checklists before action)                    │
│  ├── MCP 服务器控制内部工具访问 (MCP servers for internal tools)              │
│  └── 资源使用监控 (Resource consumption monitoring)                          │
│                                                                             │
│  核心原则：硬化环境比限制工具更重要，但工具集是最后一道防线                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**2. 确定性行为与可预测性**

Anthropic 强调：*"护栏比动机更有效"*（Guardrails work better than motivation）。限制工具集确保：

- **行为可预测性**：Agent 只能在预定义的工具集合内操作，无法执行未授权操作
- **故障模式可控**：受限的工具集减少了潜在的安全漏洞和意外行为
- **审计可追溯**：每个工具调用都可被记录和审查

**3. 资源管理与成本控制**

```
无限制工具调用的风险：                    工具集限制的收益：
┌─────────────────────────┐              ┌─────────────────────────┐
│ 无限循环调用            │              │ 明确的调用次数上限       │
│ 大规模文件读取          │    VS        │ 按需加载策略            │
│ 未受控的上下文膨胀      │              │ Token 预算管理          │
│ 昂贵的 API 调用         │              │ 成本可预测性            │
└─────────────────────────┘              └─────────────────────────┘
```

**4. 多智能体架构中的角色隔离**

根据 Anthropic 的多智能体实验（Project Vend），*"多智能体设置需要角色清晰分离"*。工具集限制强化了这种隔离：

| Agent 类型 | 工具集设计 | 目的 |
|-----------|-----------|------|
| **Independent Agent** | `create_deliverable`, `update_context` | 专注创作，受限写入 |
| **Evaluator Agent** | `evaluate`, `request_changes` | 只读评审，无写入权限 |
| **Orchestrator** | 流程控制工具 | 协调调度，不直接操作内容 |

#### 4.2.2 当前工具集分析

**Independent Agent 配置** (`agents/configs/independent_agent.yaml`):
```yaml
tools:
  - create_deliverable    # 仅写入，无读取
  - update_context        # 仅更新共享上下文
  # 缺少：read_file, read_document, search 等读取工具
```

**SDK 能力边界对比**：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Claude Agent SDK 能力边界                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SDK 原生支持的能力（需显式启用）：                                          │
│  ├─ ✅ Bash 命令执行 (bash tool)                                            │
│  ├─ ✅ 文件系统读写 (read_file, write_file, edit_file)                       │
│  ├─ ✅ 代码分析与编辑 (code analysis, regex edit)                            │
│  ├─ ✅ Web 搜索与获取 (web_search, fetch_url)                                │
│  ├─ ✅ 子智能体调用 (subagent spawning)                                      │
│  └─ ✅ 上下文管理 (128K-200K tokens, automatic compaction)                   │
│                                                                             │
│  当前 DocuSwarm 工具集限制：                                                 │
│  ├─ ❌ 无文件读取工具 - 无法主动读取 @引用文档                                │
│  ├─ ❌ 无搜索工具 - 无法在知识库中检索                                       │
│  ├─ ❌ 无 Web 访问 - 无法进行实时信息获取                                     │
│  └─ ✅ 仅保留受控的写入操作                                                   │
│                                                                             │
│  关键结论：                                                                 │
│  SDK 本身支持完整的文件操作能力，但 DocuSwarm 当前配置选择了                   │
│  限制性的工具集，这是设计决策而非技术限制。                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 4.2.3 工具集限制的双刃剑效应

**优势**：
1. **安全合规**：符合企业级部署的安全要求
2. **行为确定性**：消除 Agent 的不可预测行为
3. **简化认知负担**：Agent 不需要决定使用哪个工具

**劣势**：
1. **灵活性受限**：无法按需读取大文档（必须由外部预读注入）
2. **上下文膨胀**：所有引用文档必须在 Prompt 中预加载
3. **Token 效率低**：无法使用 RAG 等按需检索策略

#### 4.2.4 优化方向：混合工具集策略

基于 Anthropic 的推荐实践，建议采用**"分层工具集"**设计：

```yaml
# 优化后的工具集配置建议
independent_agent:
  # 核心工具（始终可用）
  core_tools:
    - create_deliverable
    - update_context
  
  # 按需工具（通过权限控制）
  conditional_tools:
    - read_document:        # 新增：按需读取 @引用文档
        description: "读取指定引用文档的完整内容"
        params:
          reference: "@docs/path/to/file.md"
        guardrail: "仅允许读取已预声明的引用文档"
    
    - search_knowledge:     # 新增：知识库检索
        description: "在已加载文档中搜索相关内容"
        params:
          query: "搜索关键词"
        guardrail: "仅在上下文不足时触发"
  
  # 严格禁止的工具
  disabled_tools:
    - bash                  # 防止命令执行
    - web_search            # 防止外部信息污染
    - write_file            # 防止任意文件写入
```

**实施建议**：

| 优先级 | 工具 | 目的 | 实现复杂度 |
|-------|------|------|----------|
| P0 | `read_document` | 允许 Agent 按需读取大文档 | 低 |
| P1 | `search_knowledge` | 在已加载文档中检索 | 中 |
| P2 | `context_summary` | 请求上下文摘要以节省 Token | 低 |
| P3 | `token_budget_check` | 主动监控 Token 使用 | 中 |

### 4.3 节点职责契约注入方式

#### 当前方式：静态注入

```
执行流程：

NodeLoader.load(node_id)
  │
  ├─ 读取 nodes/{node_id}/persona.json
  │
  └─ 构建 Persona 对象
       │
       ▼
IndependentAgent.__init__
  │
  └─ PersonaLoader.load(node_id) → 格式化 system prompt
       │
       ▼
System Prompt 包含完整 persona
  ├─ Identity
  ├─ Expertise
  └─ Principles
```

**问题**：
- Persona 是静态配置，无法根据主体上下文动态调整
- 所有项目使用相同的 persona，缺乏上下文感知

#### 建议方式：动态契约注入

```
优化后的执行流程：

NodeExecutionContext
  │
  ├─ node_id: "analyst"
  ├─ original_context: {content: "...", project_type: "fintech"}
  └─ chained_deliverables: [...]
       │
       ▼
NodePromptContractBuilder.build_independent_contract(context)
  │
  ├─ _build_persona_section(context) → 动态加载 persona
  │   ├─ 基础 persona (identity, role)
  │   ├─ 根据 project_type 选择 expertise 子集
  │   └─ 根据 chained_deliverables 添加上下文原则
  │
  └─ _build_context_section(context)
      ├─ original_context (主体上下文)
      └─ 引用文档摘要 (由 ContextResolver 预处理)
```

### 4.4 引用文档读取策略

#### 策略对比

| 策略 | 实现方式 | 优点 | 缺点 |
|------|----------|------|------|
| **A. 预读注入** (当前) | ContextResolver 预读所有 @引用，注入 PipelineState | Agent 无需额外工具，确定性高 | 上下文膨胀，可能超出 token 限制 |
| **B. Agent 主动读取** | 提供 `read_document` 工具，Agent 按需读取 | 节省 token，按需加载 | 增加 Agent 决策复杂度，需要工具调用 |
| **C. 混合策略** | 小文档预读注入，大文档提供摘要 + 按需读取 | 平衡效率和灵活性 | 实现复杂 |

#### 推荐策略：C. 混合策略

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    混合策略设计                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ContextResolver 层 (CLI/Orchestrator):                                      │
│  ├─ 解析 @引用，获取文档列表                                                 │
│  ├─ 小文档 (< 10K chars): 直接读取内容                                       │
│  ├─ 大文档 (>= 10K chars): 生成摘要 (ContextSummarizer)                      │
│  └─ 注入 PipelineState.referenced_documents                                 │
│                                                                             │
│  Independent Agent 层：                                                      │
│  ├─ 预加载：小文档内容已在 context 中                                        │
│  ├─ 按需加载：提供 read_document 工具                                        │
│  │   ├─ Agent 可根据需要读取大文档完整内容                                   │
│  │   └─ 工具参数：doc_reference (如 "@docs/spec.md")                         │
│  └─ 智能提示：提示 Agent "文档 X 有摘要，如需详细内容请使用工具"              │
│                                                                             │
│  工具定义：                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ read_document:                                                      │   │
│  │   description: 读取引用文档的完整内容                                │   │
│  │   params:                                                           │   │
│  │     reference: str  # @docs/path/to/file.md                         │   │
│  │   returns: document content or summary                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.5 节点契约优化建议

```python
# 新的 contract_builder 逻辑

class NodePromptContractBuilder:
    def _build_context_section(self, context: NodeExecutionContext) -> str:
        sections = []
        
        # 1. 主体上下文
        original = context.get("original_context", {})
        if original:
            sections.append(f"## 项目上下文\n{original.get('content', '')}")
        
        # 2. 引用文档（已预读或摘要）
        referenced = context.get("referenced_documents", [])
        if referenced:
            sections.append("\n## 参考文档")
            for doc in referenced:
                if doc.get("is_full_content"):
                    # 小文档：完整内容
                    sections.append(f"\n### {doc['reference']}\n{doc['content']}")
                else:
                    # 大文档：摘要 + 读取提示
                    sections.append(f"\n### {doc['reference']} (摘要)")
                    sections.append(f"{doc['summary']}")
                    sections.append(f"\n> 💡 如需完整内容，请使用 read_document 工具")
        
        return "\n".join(sections)
```

---

## 5. Evaluator Agent 上下文选择

### 5.1 问题核心

**当前设计**: Evaluator 接收 `original_context_summary` (原始上下文)

**问题提出**: 是否应该改为接收 `subject_context` (主体上下文)？

### 5.2 定义澄清

```
术语定义：

原始上下文 (Original Context):
├─ 来源：用户提供的 context file 内容
├─ 内容：项目需求、背景、约束等
└─ 用途：Independent Agent 创作依据

主体上下文 (Subject Context):
├─ 来源：PipelineState.subject_context
├─ 内容：原始上下文 + 流水线元数据 (pipeline_id, subject, etc.)
└─ 用途：流水线级别的上下文管理

当前 Evaluator 接收：
└─ original_context_summary ← 原始上下文的摘要
```

### 5.3 评估标准：Evaluator 需要什么？

```
Evaluator 评审三角：

        需求基准 (Requirement Baseline)
                /\
               /  \
              /    \
             /      \
            /   ?    \
           /          \
          /____________\
    交付物正文    ←→    评审标准
(Deliverable)        (Criteria)

需求基准应该是什么？
├─ A. 原始上下文 (当前) - "用户最初想要什么"
├─ B. 主体上下文 - "流水线当前状态"
└─ C. 累积上下文 - "所有上游交付物摘要"
```

### 5.4 方案对比

| 方案 | 内容 | 优点 | 缺点 |
|------|------|------|------|
| **A. 原始上下文** (当前) | context file 内容 | 评估一致性，不受流水线状态影响 | 可能缺少迭代过程中的信息 |
| **B. 主体上下文** | original + metadata | 包含流水线上下文 | metadata 对评审无实际价值 |
| **C. 累积上下文** | 所有上游交付物 | 全面了解上下文 | 违反隔离原则，影响客观性 |

### 5.5 深度分析：保持原始上下文的理由

#### 5.5.1 评审一致性

```
场景：同一项目运行两次，第二次迭代优化

如果 Evaluator 接收累积上下文：
├─ 第一次：基于原始需求评审
├─ 第二次：基于原始需求 + 第一次交付物评审
└─ 结果：两次评审标准不一致！

如果 Evaluator 仅接收原始上下文：
├─ 第一次：基于原始需求评审
├─ 第二次：仍基于原始需求评审
└─ 结果：评审标准一致，符合客观性原则
```

#### 5.5.2 隔离与客观性

```
当前设计符合三层隔离原则：

┌─────────────────────────────────────────────────────────────────────────────┐
│                    Evaluator 上下文隔离                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  EvaluatorAgentInput:                                                       │
│  ├─ ✅ original_context_summary - 需求基准（必须）                           │
│  ├─ ✅ deliverable_body - 评审对象（必须）                                   │
│  ├─ ✅ criteria - 评审标准（必须）                                          │
│  ├─ ❌ chained_deliverables - 被隔离（防止受上游影响）                       │
│  ├─ ❌ shared_context - 被隔离（防止受其他节点判断影响）                      │
│  └─ ❌ iteration_feedback - 被隔离（每轮独立评审）                           │
│                                                                             │
│  设计原则：Evaluator 应该是"盲评"，只对照原始需求和标准                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 5.5.3 实践验证

**当前代码** (`isolation.py` 第153-163行):
```python
def build_evaluator_input(...):
    # P0-2: Extract original context summary
    original_context = execution_context.get("original_context", {})
    original_summary = _extract_original_context_summary(original_context)

    return EvaluatorAgentInput(
        ...
        original_context_summary=original_summary,  # P0-2: 原始需求摘要
        ...
    )
```

**验证逻辑正确性**：
- `original_context` 来自用户 context file
- 这是"真需求"的唯一来源
- 任何其他上下文（如 shared_context）都可能被其他节点修改
- Evaluator 必须基于"真需求"评审，而非被污染的上下文

### 5.6 结论与建议

```
决策：保持当前设计 - Evaluator 使用原始上下文

理由：
1. 评审一致性 - 确保每次评审基于相同的需求基准
2. 客观性 - 防止被流水线中间状态影响
3. 隔离原则 - 符合三层隔离架构设计
4. 可追溯性 - 评审结果可直接映射到原始需求

优化建议：
1. 确保 original_context_summary 包含足够的上下文长度
   - 当前可能截断至 500 字符，考虑增加或分段注入
   
2. 添加需求追踪能力
   - Evaluator 输出增加 "requirement_coverage" 字段
   - 标记交付物覆盖了哪些原始需求

3. 考虑需求变更场景
   - 如果项目支持需求变更，应更新 original_context
   - Evaluator 应基于最新原始上下文评审
```

---

## 附录：关键决策汇总

| # | 决策 | 优先级 | 理由 |
|---|------|--------|------|
| 1 | 提取 ContextValidator | P0 | 职责分离，提升可配置性和可观测性 |
| 2 | 延迟启用 MemoryManager | P2 | 当前架构已满足需求，避免过度设计 |
| 3 | 移除 Task 契约 | P1 | 单一职责，消除重复，简化配置 |
| 4 | 添加 read_document 工具 | P1 | 支持按需读取大文档，混合策略 |
| 5 | 保持 Evaluator 原始上下文 | - | 评审一致性和客观性要求 |

---

**报告完成**

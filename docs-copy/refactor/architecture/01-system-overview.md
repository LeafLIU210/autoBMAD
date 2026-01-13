# BMAD Epic Automation 重构系统概览

**文档版本**: 1.0  
**创建日期**: 2026-01-11  
**状态**: Draft

---

## 1. 重构背景

### 1.1 当前架构问题

**核心问题：Cancel Scope 跨 Task 错误**

```
RuntimeError: Attempted to exit cancel scope in a different task
```

**问题根源**：
1. 所有 SDK 调用在同一个 Task-Main 中执行
2. 第一个 SDK 的子任务清理产生的取消状态污染 Task-Main
3. 第二个 SDK 调用继承残留状态，触发跨任务错误
4. AnyIO 与 asyncio 混用导致 CancelScope 生命周期管理混乱

### 1.2 重构目标

**技术目标**：
- 彻底消除 Cancel Scope 跨 Task 错误
- 统一使用 AnyIO 框架，消除框架混用问题
- 每个 SDK 调用在独立 TaskGroup 中隔离
- 实现结构化并发，RAII 式资源管理

**业务目标**：
- 保持业务流程语义不变
- 提升系统可靠性和稳定性
- 简化错误处理逻辑
- 支持未来扩展

---

## 2. 重构后系统架构

### 2.1 五层架构设计

```
┌─────────────────────────────────────────────────────────┐
│                   Layer 1: TaskGroup 层                  │
│              AnyIO 结构化并发容器 - 生命周期隔离          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   Layer 2: 控制器层                      │
│              业务流程决策 - 不直接调用 SDK               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    Layer 3: Agent 层                     │
│         构造 Prompt / 解释结果 / 更新状态 / 写文件        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  Layer 4: SDK 执行层                     │
│    SDKExecutor + CancellationManager + SafeClaudeSDK     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  Layer 5: Claude SDK 层                  │
│           第三方 SDK - 内部 AnyIO TaskGroup              │
└─────────────────────────────────────────────────────────┘
```

### 2.2 核心设计原则

**原则 1: 任务隔离**
- 每个 Story 处理在独立 TaskGroup 中
- 每个 SDK 调用在独立 TaskGroup 中
- 每个质量门控在独立 TaskGroup 中

**原则 2: 职责分离**
- TaskGroup 层：管理生命周期
- 控制器层：业务决策
- Agent 层：业务逻辑
- SDK 执行层：技术实现
- Claude SDK 层：第三方服务

**原则 3: 状态驱动**
- 所有决策基于核心状态值
- Agent 不做决策，只执行
- 状态是唯一真相源

**原则 4: 错误封装**
- SDK 错误不向上传播
- Cancel 状态不污染其他 Task
- 只返回业务结果

---

## 3. 业务流程架构

### 3.1 整体流程

```
Epic 启动
  ↓
SM 阶段 (Story-级 SM TaskGroup)
  └─ SMController → SMAgent → SDKExecutor → Claude
  ↓
Dev-QA 阶段 (Story-级 DevQA TaskGroup)
  └─ DevQaController
      ├─ StateAgent → SDKExecutor → Claude
      ├─ DevAgent → SDKExecutor → Claude
      └─ QAAgent → SDKExecutor → Claude
  ↓
质量门控阶段
  ├─ Ruff TaskGroup → RuffController → RuffAgent → SDKExecutor
  ├─ BasedPyright TaskGroup → PyrightController → PyrightAgent → SDKExecutor
  └─ Pytest TaskGroup → PytestController → PytestAgent → SDKExecutor
  ↓
状态同步与完成
```

### 3.2 SM 阶段架构

**目标**：Story 模板生成与初始化

**架构**：
```
EpicDriver
  ↓
SM TaskGroup (独立隔离空间)
  ↓
SMController (控制器层)
  ↓
SMAgent (Agent 层)
  ├─ 读取 Epic 内容
  ├─ 构造 SM Prompt
  ├─ 调用 SDKExecutor
  ├─ 解释 ResultMessage
  └─ 生成 Story Markdown
  ↓
SDKExecutor (SDK 执行层)
  ├─ 启动 Claude SDK
  ├─ 收集流式消息
  ├─ 检测目标结果
  ├─ 请求取消
  └─ 等待清理完成
```

### 3.3 Dev-QA 阶段架构

**目标**：状态驱动的开发-审查流水线

**架构**：
```
Story TaskGroup (Story-级隔离空间)
  ↓
DevQaController (状态机控制器)
  ↓
状态机流水线: state → dev → state → qa → state → ...
  ↓
三个独立 Agent:
  ├─ StateAgent (状态解析)
  ├─ DevAgent (开发实现)
  └─ QAAgent (质量审查)
  ↓
每个 Agent 独立调用 SDKExecutor
```

**状态机流水线（扩展版）**：
```
Step 1: State Agent 解析状态 S0
Step 2: Dev Agent 开发 (如需要)
Step 3: State Agent 解析状态 S1
Step 4: QA Agent 审查 (如需要)
Step 5: State Agent 解析状态 S2
Step 6: Dev Agent 开发 (如需要)
Step 7: State Agent 解析状态 S3
Step 8: QA Agent 审查 (如需要)
Step 9: State Agent 解析状态 S4
...
最多重复 3 轮 Dev-QA
```

### 3.4 质量门控阶段架构

**目标**：代码质量自动化检查

**架构**：
```
QualityGates TaskGroup
  ├─ Ruff TaskGroup
  │   ├─ RuffController
  │   ├─ RuffAgent
  │   └─ SDKExecutor (如需要 Claude 协助)
  │
  ├─ BasedPyright TaskGroup
  │   ├─ BasedPyrightController
  │   ├─ BasedPyrightAgent
  │   └─ SDKExecutor (如需要 Claude 协助)
  │
  └─ Pytest TaskGroup
      ├─ PytestController
      ├─ PytestAgent
      └─ SDKExecutor (如需要 Claude 协助)
```

---

## 4. 技术架构特性

### 4.1 TaskGroup 隔离机制

**旧架构问题**：
```
Task-Main (单一 Task)
  ├─ SDK-1 (在 Main 中) → 子任务污染 Main
  ├─ SDK-2 (在 Main 中) → 继承污染 ❌
  └─ SDK-3 (在 Main 中) → 继承污染 ❌
```

**新架构方案**：
```
Task-Main (仅编排)
  ├─ Story-1 TaskGroup
  │   ├─ SDK-1 TaskGroup (独立) ✅
  │   └─ SDK-2 TaskGroup (独立) ✅
  └─ Story-2 TaskGroup
      └─ SDK-3 TaskGroup (独立) ✅
```

### 4.2 Cancel Scope RAII 管理

**保证**：
- Cancel Scope 自动管理，无需手动
- 进入和退出保证在同一 Task 中
- LIFO 顺序保证
- 退出时自动清理所有子任务

**实现**：
```python
# AnyIO 提供的 RAII 模式
async with create_task_group() as tg:
    # 进入：创建 cancel scope 并 push 到栈
    await tg.start(sdk_call)
    # 退出：
    # 1. 取消所有子任务
    # 2. 等待所有子任务完成清理
    # 3. pop cancel scope
# 保证：scope 的 enter/exit 在同一 Task 中
```

### 4.3 同步点设计

**确定性同步**：
```python
# SDK 调用 1
async with create_task_group() as tg:
    result1 = await tg.start(sdk_call_1)
# 确定性同步点：sdk_call_1 完全结束

# SDK 调用 2
async with create_task_group() as tg:
    result2 = await tg.start(sdk_call_2)
# sdk_call_1 的所有清理已完成 ✅
```

---

## 5. 技术栈选择

### 5.1 框架选择：AnyIO

**选择理由**：

1. **结构化并发是必需的**
   - 生命周期管理混乱是根本问题
   - TaskGroup 提供 RAII 式资源管理
   - asyncio 需要手动管理 Task 清理

2. **Cancel Scope 是优势**
   - Level Cancellation 提供更强控制力
   - 可嵌套、可屏蔽、LIFO 保证
   - 语义清晰

3. **与 Claude SDK 统一**
   - Claude SDK 内部使用 AnyIO
   - 统一框架避免互操作问题
   - 消除 contextvars 污染

### 5.2 拒绝 Asyncio 的理由

- `asyncio.gather` 无法保证清理顺序
- `asyncio.create_task` 需手动跟踪和取消
- 缺少结构化并发原语
- 与 AnyIO 混用导致当前问题

### 5.3 拒绝 Subprocess 的理由

- 进程隔离过重，性能损失大
- 状态共享复杂
- 不符合"轻量级隔离"需求

---

## 6. 核心组件概览

### 6.1 SDKExecutor

**职责**：
- 管理单次 SDK 调用的完整生命周期
- 在独立 TaskGroup 中执行
- 提供目标检测机制
- 管理取消和清理

**接口**：
```python
class SDKExecutor:
    async def execute(
        self,
        sdk_func: Callable,
        target_predicate: Callable[[ResultMessage], bool],
        timeout: float | None = None,
        agent_name: str = "Unknown"
    ) -> SDKResult
```

### 6.2 CancellationManager

**职责**：
- 跟踪活跃的 SDK 调用
- 管理取消请求
- 验证清理完成（双条件验证）

**接口**：
```python
class CancellationManager:
    def request_cancel(self, call_id: str) -> None
    def mark_cleanup_completed(self, call_id: str) -> None
    async def confirm_safe_to_proceed(self, call_id: str) -> bool
```

### 6.3 控制器（Controller）

**职责**：
- 业务流程决策
- 基于核心状态值驱动
- 不直接调用 SDK

**类型**：
- SMController
- DevQaController
- RuffController
- BasedPyrightController
- PytestController

### 6.4 Agent

**职责**：
- 构造 SDK Prompt
- 定义目标 ResultMessage（成功条件）
- 解释 SDK 返回结果
- 更新状态 / 写文件 / 记录日志

**类型**：
- SMAgent
- StateAgent
- DevAgent
- QAAgent
- RuffAgent
- BasedPyrightAgent
- PytestAgent

---

## 7. 预期收益

### 7.1 技术收益

- **彻底消除跨 Task 错误**：结构化并发保证
- **简化代码**：减少 50% 错误处理代码
- **提升可靠性**：RAII 模式，资源泄漏不可能发生
- **更好的性能**：确定性同步点，无需时间等待

### 7.2 业务收益

- **故障隔离**：单个 Story 失败不影响其他
- **可维护性**：架构清晰，层次分明
- **可扩展性**：统一模式，易于添加新功能
- **可测试性**：每层可独立测试

---

## 8. 文档索引

### 8.1 架构文档

- [01-system-overview.md](01-system-overview.md) - 系统概览（本文档）
- [02-layer-architecture.md](02-layer-architecture.md) - 五层架构详解
- [03-taskgroup-isolation.md](03-taskgroup-isolation.md) - TaskGroup 隔离机制
- [04-controller-layer.md](04-controller-layer.md) - 控制器层设计
- [05-agent-layer.md](05-agent-layer.md) - Agent 层设计
- [06-sdk-execution-layer.md](06-sdk-execution-layer.md) - SDK 执行层设计
- [07-business-flow.md](07-business-flow.md) - 业务流程详解

### 8.2 实施方案文档

- [01-migration-strategy.md](../implementation/01-migration-strategy.md) - 迁移策略
- [02-phase1-sdk-executor.md](../implementation/02-phase1-sdk-executor.md) - Phase 1: SDK 执行层
- [03-phase2-controllers.md](../implementation/03-phase2-controllers.md) - Phase 2: 控制器层
- [04-phase3-agents.md](../implementation/04-phase3-agents.md) - Phase 3: Agent 层
- [05-phase4-integration.md](../implementation/05-phase4-integration.md) - Phase 4: 集成测试
- [06-phase5-cleanup.md](../implementation/06-phase5-cleanup.md) - Phase 5: 清理与优化
- [07-testing-strategy.md](../implementation/07-testing-strategy.md) - 测试策略
- [08-rollback-plan.md](../implementation/08-rollback-plan.md) - 回滚计划

---

**文档状态**: Draft  
**下一步**: 详细阅读各层架构文档，理解设计细节

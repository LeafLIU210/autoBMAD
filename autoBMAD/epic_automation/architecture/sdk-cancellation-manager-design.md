# SDK 取消管理器设计方案

## 📋 文档信息

- **版本**: 1.0.0
- **创建日期**: 2026-01-10
- **作者**: BMAD 团队
- **状态**: 设计阶段

## 🎯 目标与动机

### 问题背景

当前 `autoBMAD/epic_automation` 系统存在以下 SDK 取消管理问题：

1. **分散式处理**：取消逻辑分散在多个文件中（sdk_wrapper.py, dev_agent.py, qa_agent.py, epic_driver.py），违反奥卡姆剃刀原则
2. **重复代码**：每个 Agent 都实现了自己的取消处理逻辑，代码冗余
3. **缺乏监控**：无法追踪取消信号的传播路径和时序
4. **跨任务冲突**：cancel scope 跨任务访问导致 RuntimeError
5. **成功后取消**：SDK 完成后仍被取消，结果被覆盖
6. **诊断困难**：缺乏统一的取消事件日志和分析工具
7. **不安全的执行流**：Agent 在 SDK 未确认取消完成前就进入下一步

### 核心问题案例

```
Story 1.3 执行流程：
1. Dev Agent 调用 status_parser.parse_status()
2. SDK 成功执行，返回 "Ready for Development"
3. SDK 内部 Read task 被标记为 cancelled
4. CancelledError 传播到外层
5. Dev Agent 捕获异常，认为执行失败
6. Story 被标记为 cancelled

问题：SDK 实际完成了工作，但被误判为失败
```

### 设计目标

根据**奥卡姆剃刀原则**，创建统一的 SDK 取消管理器，实现：

- ✅ **唯一入口**：所有 SDK 取消必须通过管理器统一处理，移除分散的取消代码
- ✅ **强制确认**：Agent 必须等待 SDK 取消管理器确认成功后才能继续
- ✅ **集中式取消事件监控**：单一真相来源
- ✅ **Cancel scope 生命周期追踪**：完整的生命周期管理
- ✅ **跨任务冲突自动检测**：自动识别并修复
- ✅ **成功后取消的智能识别**：区分真正失败和误判
- ✅ **完整的诊断报告生成**：可追溯的审计日志
- ✅ **清理过程的可观测性**：实时监控清理状态

## 🏗️ 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                   SDK Cancellation Manager                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Core Components                              │  │
│  │  ┌─────────────────┐  ┌─────────────────┐               │  │
│  │  │ Cancel Scope    │  │ Resource        │               │  │
│  │  │ Tracker         │  │ Monitor         │               │  │
│  │  └─────────────────┘  └─────────────────┘               │  │
│  │  ┌─────────────────┐  ┌─────────────────┐               │  │
│  │  │ Async           │  │ Event           │               │  │
│  │  │ Debugger        │  │ Aggregator      │               │  │
│  │  └─────────────────┘  └─────────────────┘               │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Management Layer                             │  │
│  │  • SDK Call Tracking      • Result Caching               │  │
│  │  • Cancellation Detection • Cross-task Validation        │  │
│  │  • Cleanup Coordination   • Report Generation            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     Integration Points                   │
        ├─────────────────────────────────────────┤
        │  • SafeClaudeSDK                        │
        │  • DevAgent / QAAgent / SMAgent         │
        │  • StateManager                          │
        │  • EpicDriver                           │
        └─────────────────────────────────────────┘
```

### 目录结构

```
autoBMAD/epic_automation/
├── monitoring/                          # 新建监控模块
│   ├── __init__.py                      # 模块导出
│   ├── cancel_scope_tracker.py         # Cancel scope 追踪器
│   ├── resource_monitor.py             # 资源监控器
│   ├── async_debugger.py               # 异步调试器
│   ├── sdk_cancellation_manager.py     # 统一管理器（核心）
│   └── event_aggregator.py             # 事件聚合器
├── sdk_wrapper.py                       # 修改：集成管理器
├── dev_agent.py                         # 修改：使用管理器
├── qa_agent.py                          # 修改：使用管理器
└── epic_driver.py                       # 修改：使用管理器
```

## 🔧 核心组件设计

### 1. SDKCancellationManager（核心管理器）

#### 职责

- **唯一管理入口**：作为 `autoBMAD/epic_automation` 中所有 SDK 取消的统一管理者
- **强制执行流程**：确保 Agent 等待取消确认后才能继续执行
- **统一追踪所有 SDK 执行调用**：记录所有 SDK 生命周期事件
- **监控取消信号传播**：追踪信号在组件间的传播路径
- **检测"成功后取消"场景**：智能识别并抑制误判
- **协调资源清理**：确保清理完成后才允许继续
- **生成诊断报告**：提供完整的审计追踪

#### 关键接口

```python
class SDKCancellationManager:
    """SDK 取消管理器"""
    
    # 初始化
    def __init__(self, log_dir: Path, enable_tracking: bool = True)
    
    # 追踪 SDK 执行
    @asynccontextmanager
    async def track_sdk_execution(
        self, 
        call_id: str, 
        operation_name: str,
        context: Dict[str, Any]
    ) -> AsyncIterator[Dict[str, Any]]
    
    # 标记结果已接收
    def mark_result_received(self, call_id: str, result: Any)
    
    # 检查取消类型
    def check_cancellation_type(
        self, 
        call_id: str
    ) -> Literal["before_completion", "after_success", "unknown"]
    
    # 🎯 核心方法：等待取消完成（强制同步点）
    async def wait_for_cancellation_complete(
        self,
        call_id: str,
        timeout: float = 5.0
    ) -> bool
    
    # 🎯 核心方法：确认 SDK 可以安全继续
    def confirm_safe_to_proceed(self, call_id: str) -> bool
    
    # 生成诊断报告
    def generate_report(self) -> Dict[str, Any]
    
    # 获取统计信息
    def get_statistics(self) -> Dict[str, Any]
```

#### 状态追踪

```python
# 每个 SDK 调用的追踪信息
{
    "call_id": "dev_agent_parse_status_001",
    "operation": "parse_status",
    "scope_id": "uuid-xxx",
    "start_time": datetime,
    "end_time": datetime,
    "duration": 3.52,  # seconds
    "status": "completed" | "cancelled" | "failed",
    "result": Any,
    "result_received_at": datetime,  # 关键：结果接收时间
    "exception": str,
    "cancel_type": "after_success" | "before_completion",
    "context": {
        "agent": "dev_agent",
        "story_path": "...",
        "iteration": 1
    }
}
```

### 2. CancelScopeTracker（Cancel Scope 追踪器）

#### 职责

- 追踪 cancel scope 的进入/退出
- 检测跨任务访问
- 记录 scope 层级关系
- 识别 scope 泄漏

#### 关键特性

```python
# 跨任务检测示例
tracker.enter_scope(scope_id="scope_001", name="sdk_execution")
# Task A 进入

# ... 异步操作 ...

tracker.exit_scope(scope_id="scope_001")
# Task B 退出 ❌ 跨任务访问！

# 自动记录错误事件
{
    "event_type": "error",
    "error_type": "cross_task_access",
    "scope_id": "scope_001",
    "entered_by_task": "Task-12345",
    "exited_by_task": "Task-67890",
    "stack_trace": "..."
}
```

### 3. ResourceMonitor（资源监控器）

#### 职责

- 监控锁的获取/释放
- 追踪 SDK 会话生命周期
- 检测资源泄漏
- 统计资源使用情况

#### 监控项

```python
# 锁监控
resource_monitor.track_lock_acquisition("sdk_session_lock")
# ... 执行操作 ...
resource_monitor.track_lock_release("sdk_session_lock")

# SDK 会话监控
resource_monitor.track_sdk_session(
    session_id="session_001",
    status="created" | "executing" | "completed" | "cancelled"
)

# 生成资源报告
{
    "locks": {
        "total_acquired": 15,
        "avg_duration": 0.32,
        "max_duration": 2.15,
        "leaked_locks": []
    },
    "sdk_sessions": {
        "total_sessions": 8,
        "active_sessions": 1,
        "completed_sessions": 6,
        "cancelled_sessions": 1
    }
}
```

### 4. EventAggregator（事件聚合器）

#### 职责

- 聚合来自多个组件的事件
- 时序分析
- 关联事件链
- 生成统一时间线

#### 事件类型

```python
# 事件定义
class Event:
    timestamp: datetime
    event_type: str  # "sdk_start", "sdk_complete", "cancel_signal", "scope_enter", ...
    source: str      # "SafeClaudeSDK", "DevAgent", "CancelScopeTracker", ...
    call_id: str
    details: Dict[str, Any]

# 时间线示例
[
    {"time": "09:57:56.296", "event": "sdk_start", "source": "SafeClaudeSDK"},
    {"time": "09:58:00.001", "event": "sdk_complete", "source": "SafeClaudeSDK", "result": "Ready for Development"},
    {"time": "09:58:00.001", "event": "cancel_signal", "source": "claude_agent_sdk", "reason": "Read task cancelled"},
    {"time": "09:58:00.001", "event": "cancellation_propagated", "source": "SafeClaudeSDK"}
]
```

## 🔌 集成方案

### SafeClaudeSDK 集成

#### 修改前（分散的取消处理 - 违反奥卡姆剃刀原则）

```python
async def execute(self) -> bool:
    try:
        result = await self._execute_safely()
        return result
    except asyncio.CancelledError:
        logger.warning("SDK execution was cancelled")  # ❌ 各处理各的
        raise  # ❌ 直接抛出，没有统一管理
```

#### 修改后（统一管理 - 符合奥卡姆剃刀原则）

```python
async def execute(self) -> bool:
    """通过统一管理器执行 SDK - 唯一入口"""
    from autoBMAD.epic_automation.monitoring import get_cancellation_manager
    
    manager = get_cancellation_manager()
    call_id = f"sdk_{id(self)}_{int(time.time() * 1000)}"
    
    # 🎯 所有 SDK 执行都必须通过管理器追踪
    async with manager.track_sdk_execution(
        call_id=call_id,
        operation_name="sdk_execute",
        context={"prompt_length": len(self.prompt)}
    ) as call_info:
        try:
            result = await self._execute_safely()
            
            # 🎯 立即标记结果已接收
            if result:
                manager.mark_result_received(call_id, result)
            
            return result
            
        except asyncio.CancelledError:
            # 🎯 统一处理：让管理器决定如何响应
            cancel_type = manager.check_cancellation_type(call_id)
            
            if cancel_type == "after_success":
                # 管理器确认工作已完成，安全忽略取消
                logger.info(
                    "[SDK] Cancellation suppressed by manager - work completed"
                )
                return True
            else:
                # 管理器确认是真正的取消
                logger.warning("SDK cancelled before completion (confirmed by manager)")
                raise
```

**关键改进（奥卡姆剃刀原则）：**
1. ❌ **移除**：sdk_wrapper.py 中的独立取消处理逻辑
2. ✅ **统一**：所有取消判断由管理器完成
3. ✅ **简化**：SDK 只需调用管理器，不再自行判断

### DevAgent 集成

#### 修改前（分散处理 - 违反奥卡姆剃刀原则）

```python
async def execute(self, story_path: str) -> bool:
    try:
        story_status = await self.status_parser.parse_status(content)
        return True  # ❌ 没有等待 SDK 取消确认就继续
    except Exception as e:
        logger.error(f"Dev phase failed: {e}")  # ❌ 各自处理异常
        return False
```

#### 修改后（统一管理 - 符合奥卡姆剃刀原则）

```python
async def execute(self, story_path: str) -> bool:
    """开发执行流程 - 强制通过管理器处理所有 SDK 取消"""
    from autoBMAD.epic_automation.monitoring import get_cancellation_manager
    
    manager = get_cancellation_manager()
    call_id = f"dev_parse_{story_path}_{int(time.time())}"
    
    try:
        # 🎯 所有 SDK 调用都必须通过管理器
        async with manager.track_sdk_execution(
            call_id=call_id,
            operation_name="parse_status",
            context={"story": story_path, "agent": "dev"}
        ):
            story_status = await self.status_parser.parse_status(content)
        
        # 🎯 关键：等待管理器确认 SDK 已完全清理
        await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
        
        # 🎯 只有在管理器确认安全后才能继续
        if not manager.confirm_safe_to_proceed(call_id):
            logger.warning("Manager blocked continuation - SDK not fully cleaned")
            return False
        
        return True
        
    except asyncio.CancelledError:
        # 🎯 统一处理：完全委托给管理器
        cancel_type = manager.check_cancellation_type(call_id)
        
        if cancel_type == "after_success":
            # 等待清理完成
            await manager.wait_for_cancellation_complete(call_id)
            logger.info("Dev phase completed (confirmed by manager)")
            return True
        
        logger.warning("Dev phase cancelled (confirmed by manager)")
        raise
        
    except Exception as e:
        logger.error(f"Dev phase failed: {e}")
        return False
```

**关键改进（奥卡姆剃刀原则）：**
1. ❌ **移除**：dev_agent.py 中的独立取消判断代码
2. ✅ **强制同步**：必须等待 `wait_for_cancellation_complete()` 完成
3. ✅ **安全检查**：通过 `confirm_safe_to_proceed()` 确认可以继续
4. ✅ **统一决策**：所有判断由管理器完成，Agent 只执行

## 📊 诊断报告格式

### 完整报告结构

```json
{
  "metadata": {
    "generated_at": "2026-01-10T10:00:00",
    "report_version": "1.0.0",
    "system_version": "BMAD 2.0.0"
  },
  "summary": {
    "total_sdk_calls": 25,
    "successful_completions": 20,
    "cancellations": 3,
    "cancel_after_success": 2,
    "failures": 2,
    "success_rate": 0.80,
    "cross_task_violations": 1
  },
  "timeline": [
    {
      "timestamp": "09:57:56.296",
      "event": "sdk_execution_started",
      "call_id": "dev_parse_1.3",
      "operation": "parse_status",
      "agent": "dev_agent"
    },
    {
      "timestamp": "09:58:00.001",
      "event": "sdk_result_received",
      "call_id": "dev_parse_1.3",
      "result": "Ready for Development"
    },
    {
      "timestamp": "09:58:00.001",
      "event": "cancellation_detected",
      "call_id": "dev_parse_1.3",
      "cancel_type": "after_success",
      "action_taken": "suppressed"
    }
  ],
  "cancel_scope_analysis": {
    "total_scopes": 15,
    "active_scopes": 0,
    "cross_task_violations": [
      {
        "scope_id": "scope_001",
        "entered_by_task": "Task-12345",
        "exited_by_task": "Task-67890",
        "error_message": "Cross-task cancel scope access detected"
      }
    ]
  },
  "resource_usage": {
    "locks": {
      "total_acquired": 15,
      "avg_duration": 0.32,
      "leaked_locks": []
    },
    "sdk_sessions": {
      "total": 8,
      "completed": 6,
      "cancelled": 1,
      "failed": 1
    }
  },
  "cancellation_details": [
    {
      "call_id": "dev_parse_1.3",
      "operation": "parse_status",
      "cancel_type": "after_success",
      "result_available": true,
      "result": "Ready for Development",
      "duration": 3.705,
      "timeline": {
        "start": "09:57:56.296",
        "result_received": "09:58:00.001",
        "cancelled_at": "09:58:00.001"
      },
      "recommendation": "Suppress cancellation - work completed successfully"
    }
  ],
  "recommendations": [
    "1 cancellation occurred after successful completion - consider suppressing",
    "1 cross-task violation detected - review task isolation",
    "Overall success rate is healthy at 80%"
  ]
}
```

### 实时监控输出

```
═══════════════════════════════════════════════════════════════
              SDK Cancellation Manager - Live Status
═══════════════════════════════════════════════════════════════
[10:00:15] Statistics:
  Total SDK Calls:      25
  Successful:           20 (80.0%)
  Cancelled:            3 (12.0%)
    └─ After Success:   2 (8.0%)  ⚠️
  Failed:               2 (8.0%)
  
[10:00:15] Active Operations: 1
  • dev_parse_1.4 (parse_status) - Running for 2.3s

[10:00:15] Cancel Scope Status:
  Active Scopes:        1
  Cross-task Violations: 1  ❌

[10:00:15] Recent Events:
  [09:58:00] SDK Result: "Ready for Development"
  [09:58:00] Cancellation after success (suppressed)
  [09:58:00] Story 1.3 marked as cancelled ❌

[10:00:15] Alerts:
  ⚠️  2 successful operations were cancelled
  ❌  1 cross-task cancel scope violation detected
═══════════════════════════════════════════════════════════════
```

## 🚀 实施计划

### Phase 1: 基础设施搭建（1-2天）

**任务：**
1. 从 `BUGFIX_20260107/enhanced_debug_suite/` 迁移核心组件
2. 创建 `autoBMAD/epic_automation/monitoring/` 目录
3. 实现 `SDKCancellationManager` 核心类
4. 添加单元测试

**交付物：**
- `monitoring/` 模块完整代码
- 单元测试覆盖率 > 80%
- 基础文档

### Phase 2: SafeClaudeSDK 集成（1天）

**任务：**
1. 修改 `sdk_wrapper.py` 集成管理器
2. 实现结果接收标记机制
3. 实现"成功后取消"检测
4. 添加集成测试

**验证点：**
- Story 1.3 场景不再误判为失败
- 取消事件被正确记录
- 诊断报告生成正常

### Phase 3: Agent 层集成（1天）

**任务：**
1. 修改 `dev_agent.py` 使用管理器
2. 修改 `qa_agent.py` 使用管理器
3. 修改 `sm_agent.py` 使用管理器
4. 添加端到端测试

**验证点：**
- 所有 Agent 的 SDK 调用被追踪
- 取消信号正确传播
- 跨任务冲突被检测

### Phase 4: 监控与诊断（1天）

**任务：**
1. 实现实时监控输出
2. 实现诊断报告生成
3. 添加可视化仪表板（可选）
4. 性能优化

**交付物：**
- 完整的诊断报告
- 实时监控界面
- 性能基准测试

### Phase 5: 文档与培训（0.5天）

**任务：**
1. 编写使用文档
2. 编写故障排查指南
3. 代码注释完善
4. 团队培训

**交付物：**
- 使用文档
- 故障排查指南
- 最佳实践文档

## 📈 性能考虑

### 开销分析

| 操作 | 预估开销 | 影响 |
|------|---------|------|
| Enter/Exit Scope | ~0.1ms | 可忽略 |
| Event Logging | ~0.5ms | 低 |
| Report Generation | ~50ms | 仅在需要时 |
| 实时监控 | ~1ms/s | 低 |

### 优化策略

1. **异步日志写入**：使用后台任务写入日志
2. **事件批处理**：每 100 个事件批量写入
3. **可配置跟踪级别**：
   - `MINIMAL`: 仅记录错误
   - `NORMAL`: 记录所有 SDK 调用（默认）
   - `VERBOSE`: 记录所有事件
4. **内存管理**：限制内存事件数量（最多 10000 个）

## 🧪 测试策略

### 单元测试

```python
# test_sdk_cancellation_manager.py
async def test_track_successful_execution():
    """测试成功执行追踪"""
    manager = SDKCancellationManager()
    
    async with manager.track_sdk_execution("test_001", "test_op") as call_info:
        manager.mark_result_received("test_001", "success_result")
    
    assert manager.stats["successful_completions"] == 1
    assert manager.stats["cancellations"] == 0

async def test_cancel_after_success_detection():
    """测试成功后取消检测"""
    manager = SDKCancellationManager()
    
    async with manager.track_sdk_execution("test_002", "test_op") as call_info:
        manager.mark_result_received("test_002", "result")
        raise asyncio.CancelledError()
    
    assert manager.stats["cancel_after_success"] == 1
    cancel_type = manager.check_cancellation_type("test_002")
    assert cancel_type == "after_success"
```

### 集成测试

```python
# test_integration_with_sdk_wrapper.py
async def test_sdk_wrapper_integration():
    """测试 SafeClaudeSDK 集成"""
    from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK
    from autoBMAD.epic_automation.monitoring import get_cancellation_manager
    
    manager = get_cancellation_manager()
    sdk = SafeClaudeSDK(prompt="test", options=...)
    
    result = await sdk.execute()
    
    # 验证追踪记录
    stats = manager.get_statistics()
    assert stats["total_sdk_calls"] >= 1
```

### 端到端测试

```python
# test_e2e_story_processing.py
async def test_story_1_3_scenario():
    """测试 Story 1.3 场景（成功后取消）"""
    driver = EpicDriver(epic_path="docs/epics/epic-1.md")
    
    # 执行 Story 1.3
    result = await driver.process_story(story_1_3)
    
    # 验证不再误判为失败
    assert result == True
    
    # 验证取消被正确处理
    manager = get_cancellation_manager()
    report = manager.generate_report()
    assert report["summary"]["cancel_after_success"] >= 0
```

## 🔒 安全与隐私

### 敏感信息处理

1. **Prompt 内容**：仅记录长度，不记录完整内容
2. **结果数据**：仅记录前 100 字符
3. **路径信息**：相对路径替代绝对路径
4. **API Keys**：永不记录

### 日志保留策略

- 实时日志：保留 7 天
- 诊断报告：保留 30 天
- 错误日志：保留 90 天
- 自动清理旧日志

## 🎓 最佳实践

### 使用建议

1. **始终使用上下文管理器**
   ```python
   async with manager.track_sdk_execution(...):
       # SDK 调用
   ```

2. **及时标记结果接收**
   ```python
   result = await sdk.execute()
   if result:
       manager.mark_result_received(call_id, result)
   ```

3. **定期生成报告**
   ```python
   # 在每个 Epic 完成后
   report = manager.generate_report()
   save_report(report)
   ```

4. **监控关键指标**
   - `cancel_after_success` 比率应 < 5%
   - `cross_task_violations` 应为 0
   - `success_rate` 应 > 90%

### 故障排查流程

```
1. 检查实时监控输出
   ↓
2. 生成诊断报告
   ↓
3. 查看 timeline 确定问题时序
   ↓
4. 检查 cancel_scope_analysis 查找跨任务冲突
   ↓
5. 查看 cancellation_details 了解取消类型
   ↓
6. 根据 recommendations 采取行动
```

## 📚 参考资料

### 相关文档

- [ASYNC_CANCEL_SCOPE_FIX.md](../../ASYNC_CANCEL_SCOPE_FIX.md)
- [BUGFIX_20260109.md](../../BUGFIX_20260109.md)
- [sdk_wrapper.py 源码分析](../evaluation/sdk-wrapper-analysis.md)

### 外部资源

- [Python asyncio 取消机制](https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.cancel)
- [AnyIO Cancel Scopes](https://anyio.readthedocs.io/en/stable/cancellation.html)

## 📝 变更记录

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| 1.0.0 | 2026-01-10 | 初始版本 | BMAD 团队 |

## ✅ 验收标准

### 功能验收

- [ ] 所有 SDK 调用被追踪
- [ ] "成功后取消"正确检测并处理
- [ ] 跨任务冲突自动识别
- [ ] 诊断报告生成正常
- [ ] 实时监控正常工作

### 性能验收

- [ ] 单次追踪开销 < 1ms
- [ ] 内存占用 < 100MB
- [ ] 不影响正常执行流程

### 质量验收

- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试全部通过
- [ ] 端到端测试覆盖主要场景
- [ ] 代码审查通过
- [ ] 文档完整

## 🚦 当前状态

- **设计阶段**: ✅ 完成
- **实施阶段**: ⏳ 待开始
- **测试阶段**: ⏳ 待开始
- **部署阶段**: ⏳ 待开始

---

**下一步行动**: 开始 Phase 1 实施

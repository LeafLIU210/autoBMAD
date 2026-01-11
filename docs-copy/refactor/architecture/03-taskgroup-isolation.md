# TaskGroup 隔离机制详解

**文档版本**: 1.0  
**创建日期**: 2026-01-11  
**状态**: Draft

---

## 1. TaskGroup 基础

### 1.1 什么是 TaskGroup

**定义**：AnyIO 提供的结构化并发原语，用于管理一组相关的异步任务。

**核心特性**：
1. **RAII 模式**：通过 `async with` 自动管理生命周期
2. **结构化并发**：父任务等待所有子任务完成
3. **自动取消**：退出时自动取消所有未完成任务
4. **异常传播**：子任务异常会传播到父任务

### 1.2 TaskGroup vs asyncio.gather

| 特性 | TaskGroup (AnyIO) | asyncio.gather |
|------|-------------------|----------------|
| 生命周期管理 | 自动 RAII | 手动管理 |
| 取消传播 | 自动 | 需手动传播 |
| 异常处理 | 结构化 | 需手动聚合 |
| 资源清理 | 保证清理 | 可能泄漏 |
| 嵌套支持 | 原生支持 | 复杂 |

---

## 2. 隔离机制原理

### 2.1 Cancel Scope 隔离

**问题根源**（旧架构）：
```python
# ❌ 所有在同一 Task 中
async def bad_pattern():
    # Task-Main
    result1 = await sdk_call_1()  # 创建 Task-2, Task-3
    # Task-2 清理时污染 Task-Main 的 cancel scope
    result2 = await sdk_call_2()  # 继承污染，立即失败 ❌
```

**隔离方案**（新架构）：
```python
# ✅ 每个 SDK 调用独立 TaskGroup
async def good_pattern():
    # SDK 调用 1
    async with create_task_group() as tg1:
        result1 = await tg1.start(sdk_call_1)
    # 退出时保证 Task-2, Task-3 完全清理 ✅
    
    # SDK 调用 2 (全新上下文)
    async with create_task_group() as tg2:
        result2 = await tg2.start(sdk_call_2)
    # 无污染 ✅
```

### 2.2 上下文变量隔离

**contextvars 传播问题**：
```python
import contextvars

cancel_flag = contextvars.ContextVar('cancel_requested')

# ❌ 旧架构：上下文在 Task 间传播
async def bad_pattern():
    cancel_flag.set(True)  # Task-Main 设置
    await sdk_call_2()     # 继承 Task-Main 的上下文 ❌
```

**TaskGroup 隔离**：
```python
# ✅ 新架构：TaskGroup 创建新的执行上下文
async def good_pattern():
    async with create_task_group() as tg1:
        cancel_flag.set(True)
        await tg1.start(sdk_call_1)
    # 退出时上下文随 TaskGroup 销毁
    
    async with create_task_group() as tg2:
        # 全新上下文，cancel_flag 未设置 ✅
        await tg2.start(sdk_call_2)
```

### 2.3 资源生命周期隔离

**资源泄漏问题**（旧架构）：
```python
# ❌ 手动管理，容易泄漏
async def bad_pattern():
    task1 = asyncio.create_task(sdk_call_1())
    try:
        result = await task1
    finally:
        if not task1.done():
            task1.cancel()  # 可能忘记
            try:
                await task1  # 可能忘记等待
            except asyncio.CancelledError:
                pass
```

**TaskGroup 自动管理**：
```python
# ✅ RAII 模式，自动清理
async def good_pattern():
    async with create_task_group() as tg:
        result = await tg.start(sdk_call_1)
    # 退出时自动：
    # 1. 取消所有未完成任务
    # 2. 等待所有任务清理完成
    # 3. 释放所有资源
```

---

## 3. 三层隔离架构

### 3.1 Level 1: Story 隔离

**目标**：不同 Story 之间完全隔离

**实现**：
```python
async def process_stories(stories: list[str]):
    """顺序处理所有 Story"""
    for story_path in stories:
        # 每个 Story 独立 TaskGroup
        async with create_task_group() as story_tg:
            result = await process_single_story(story_tg, story_path)
        # Story-1 完成清理后，才开始 Story-2 ✅
```

**隔离保证**：
- Story-1 的 SDK 调用不影响 Story-2
- Story-1 的错误不传播到 Story-2
- Story-1 的资源完全清理后，Story-2 才开始

### 3.2 Level 2: Agent 隔离 (可选)

**目标**：同一 Story 内不同 Agent 隔离

**实现**：
```python
async def process_single_story(story_tg: TaskGroup, story_path: str):
    """在 Story TaskGroup 中处理单个 Story"""
    
    # 状态解析 (独立子 TaskGroup)
    async with create_task_group() as state_tg:
        status = await parse_status(state_tg, story_path)
    
    # 开发执行 (独立子 TaskGroup)
    if status == "Ready for Development":
        async with create_task_group() as dev_tg:
            await develop(dev_tg, story_path)
    
    # QA 审查 (独立子 TaskGroup)
    async with create_task_group() as qa_tg:
        await review(qa_tg, story_path)
```

**说明**：
- 这一层隔离是可选的
- 大多数情况下，在 Story TaskGroup 内顺序执行即可
- 只有在需要更强隔离时才使用

### 3.3 Level 3: SDK 调用隔离

**目标**：每个 SDK 调用完全隔离

**实现**：
```python
async def execute_sdk_call(agent_name: str, sdk_func: Callable) -> SDKResult:
    """在独立 TaskGroup 中执行 SDK 调用"""
    async with create_task_group() as sdk_tg:
        # SDK 调用在最内层 TaskGroup
        messages = []
        call_id = str(uuid.uuid4())
        
        try:
            # 启动流式调用
            async for msg in sdk_func():
                messages.append(msg)
                
                # 检测目标
                if is_target_message(msg):
                    # 请求取消
                    request_cancel(call_id)
                    break
            
            # 等待清理完成
            await confirm_cleanup_completed(call_id)
            
            return SDKResult(
                has_target_result=True,
                cleanup_completed=True,
                messages=messages
            )
        
        except Exception as e:
            # 所有异常都封装在结果中
            return SDKResult(
                has_target_result=False,
                errors=[str(e)]
            )
    # 退出时保证 Claude SDK 内部任务已清理
```

---

## 4. 隔离边界设计

### 4.1 物理边界

**定义**：通过 TaskGroup 创建的执行边界

**边界类型**：
```
Epic Level (进程级)
  ├─ Story-1 TaskGroup (Story 级)
  │   ├─ SM TaskGroup (阶段级)
  │   └─ DevQA TaskGroup (阶段级)
  │       ├─ StateAgent SDK TaskGroup (调用级)
  │       ├─ DevAgent SDK TaskGroup (调用级)
  │       └─ QAAgent SDK TaskGroup (调用级)
  └─ Story-2 TaskGroup (Story 级)
```

### 4.2 逻辑边界

**定义**：通过职责划分的逻辑边界

**边界类型**：
```
EpicDriver (编排层)
  ↓ 不能跨越
Controller (决策层)
  ↓ 不能跨越
Agent (业务层)
  ↓ 不能跨越
SDK Executor (技术层)
  ↓ 不能跨越
Claude SDK (服务层)
```

### 4.3 状态边界

**定义**：通过核心状态值传递的信息边界

**规则**：
- ✅ Agent 通过核心状态值通信（间接）
- ❌ Agent 不能直接调用其他 Agent

**示例**：
```python
# ✅ 正确：通过状态通信
# DevAgent
self._update_story_status(story_path, "Ready for Review")

# QAAgent (在另一个 SDK TaskGroup 中)
status = self._read_story_status(story_path)
if status == "Ready for Review":
    await self.execute(story_path)

# ❌ 错误：直接调用
# DevAgent
await self.qa_agent.execute(story_path)  # 跨边界调用
```

---

## 5. 隔离级别配置

### 5.1 强隔离模式

**适用场景**：生产环境、稳定性优先

**配置**：
```python
class IsolationConfig:
    story_level_isolation = True      # Story 独立 TaskGroup
    agent_level_isolation = True      # Agent 独立 TaskGroup
    sdk_level_isolation = True        # SDK 独立 TaskGroup
    parallel_stories = False          # Story 顺序执行
    parallel_agents = False           # Agent 顺序执行
```

**特点**：
- 最强隔离
- 最高可靠性
- 较慢性能

### 5.2 标准隔离模式 (推荐)

**适用场景**：日常开发、平衡性能和可靠性

**配置**：
```python
class IsolationConfig:
    story_level_isolation = True      # Story 独立 TaskGroup
    agent_level_isolation = False     # Agent 在 Story TaskGroup 内顺序执行
    sdk_level_isolation = True        # SDK 独立 TaskGroup
    parallel_stories = False          # Story 顺序执行
    parallel_agents = False           # Agent 顺序执行
```

**特点**：
- 平衡隔离
- 良好可靠性
- 合理性能

### 5.3 弱隔离模式

**适用场景**：测试环境、性能优先

**配置**：
```python
class IsolationConfig:
    story_level_isolation = True      # Story 独立 TaskGroup
    agent_level_isolation = False     # Agent 顺序执行
    sdk_level_isolation = True        # SDK 独立 TaskGroup
    parallel_stories = True           # Story 并行执行
    parallel_agents = False           # Agent 顺序执行
```

**特点**：
- 基础隔离
- 最快性能
- 需要更多测试

---

## 6. 隔离验证

### 6.1 隔离性测试

**测试目标**：验证 TaskGroup 之间完全隔离

**测试方法**：
```python
async def test_taskgroup_isolation():
    """测试 TaskGroup 隔离性"""
    
    # 测试 1: Cancel 状态不传播
    async with create_task_group() as tg1:
        # 在 tg1 中设置取消状态
        tg1.cancel_scope.cancel()
    
    # tg1 退出后，取消状态已清理
    async with create_task_group() as tg2:
        # tg2 应该是全新状态
        assert not tg2.cancel_scope.cancel_called
    
    # 测试 2: 上下文变量不传播
    test_var = contextvars.ContextVar('test')
    
    async with create_task_group() as tg1:
        test_var.set("value1")
    
    async with create_task_group() as tg2:
        # tg2 应该看不到 tg1 的上下文
        assert test_var.get(None) is None
```

### 6.2 资源清理验证

**测试目标**：验证 TaskGroup 退出时资源完全清理

**测试方法**：
```python
async def test_resource_cleanup():
    """测试资源清理完整性"""
    
    active_tasks_before = len(anyio.get_current_task().parent_task_group._tasks)
    
    async with create_task_group() as tg:
        # 创建多个子任务
        await tg.start(task1)
        await tg.start(task2)
        await tg.start(task3)
    
    active_tasks_after = len(anyio.get_current_task().parent_task_group._tasks)
    
    # TaskGroup 退出后，所有子任务都应清理
    assert active_tasks_after == active_tasks_before
```

### 6.3 异常传播验证

**测试目标**：验证异常正确传播和隔离

**测试方法**：
```python
async def test_exception_propagation():
    """测试异常传播机制"""
    
    # 测试 1: 异常向上传播
    with pytest.raises(ValueError):
        async with create_task_group() as tg:
            async def failing_task():
                raise ValueError("Task failed")
            
            await tg.start(failing_task)
    
    # 测试 2: 异常不横向传播
    result2 = None
    async with create_task_group() as tg2:
        async def success_task():
            return "success"
        
        result2 = await tg2.start(success_task)
    
    # tg2 应该正常执行，不受 tg1 异常影响
    assert result2 == "success"
```

---

## 7. 隔离模式最佳实践

### 7.1 DO（应该做的）

**1. 使用 TaskGroup 创建隔离边界**
```python
# ✅ 正确
async with create_task_group() as tg:
    result = await tg.start(isolated_task)
```

**2. 每个 SDK 调用在独立 TaskGroup 中**
```python
# ✅ 正确
async def execute_sdk():
    async with create_task_group() as sdk_tg:
        result = await sdk_tg.start(claude_sdk_call)
        return result
```

**3. 使用 RAII 模式管理资源**
```python
# ✅ 正确
async with create_task_group() as tg:
    # 资源自动管理
    pass
# 退出时自动清理
```

### 7.2 DON'T（不应该做的）

**1. 不要手动管理 Task**
```python
# ❌ 错误
task = anyio.create_task(some_coro)
try:
    result = await task
finally:
    task.cancel()
```

**2. 不要跨 TaskGroup 传递 CancelScope**
```python
# ❌ 错误
async with create_task_group() as tg1:
    scope = tg1.cancel_scope

async with create_task_group() as tg2:
    # 不要使用 tg1 的 scope
    scope.cancel()  # 跨 TaskGroup 操作 ❌
```

**3. 不要在 TaskGroup 外等待子任务**
```python
# ❌ 错误
async def bad_pattern():
    task = None
    async with create_task_group() as tg:
        task = tg.start_soon(some_coro)
    
    # TaskGroup 已退出，但尝试等待子任务
    await task  # ❌ 错误
```

---

## 8. 性能考虑

### 8.1 TaskGroup 开销

**创建开销**：
- TaskGroup 创建: ~10μs
- Cancel Scope 创建: ~5μs
- 上下文切换: ~1μs

**结论**：开销极小，可以频繁创建

### 8.2 隔离级别与性能

| 隔离级别 | 创建次数 | 开销 | 性能影响 |
|----------|----------|------|----------|
| Story 级 | ~5/epic | 极小 | <1% |
| Agent 级 | ~15/story | 小 | ~2% |
| SDK 级 | ~30/story | 中等 | ~5% |

**结论**：隔离开销可接受，可靠性收益远大于性能损失

### 8.3 优化策略

**策略 1: 合并短生命周期任务**
```python
# 如果多个操作都很短，可以在同一 TaskGroup 中
async with create_task_group() as tg:
    result1 = await tg.start(short_task_1)
    result2 = await tg.start(short_task_2)
    result3 = await tg.start(short_task_3)
```

**策略 2: 使用标准隔离模式**
```python
# 不需要 Agent 级隔离
async with create_task_group() as story_tg:
    # Agent 在 Story TaskGroup 内顺序执行
    await state_agent.execute()
    await dev_agent.execute()
    await qa_agent.execute()
```

---

## 9. 故障排查

### 9.1 常见问题

**问题 1: RuntimeError: Attempted to exit cancel scope in a different task**

**原因**：跨 TaskGroup 操作 CancelScope

**解决**：确保每个 SDK 调用在独立 TaskGroup 中

**问题 2: 资源泄漏**

**原因**：手动管理 Task 未正确清理

**解决**：使用 TaskGroup RAII 模式

**问题 3: 异常未传播**

**原因**：捕获异常但未重新抛出

**解决**：让 TaskGroup 自动处理异常传播

### 9.2 调试技巧

**技巧 1: 打印 TaskGroup 栈**
```python
import anyio

async def debug_taskgroup():
    task = anyio.get_current_task()
    print(f"Current task: {task}")
    print(f"Task group: {task.parent_task_group}")
```

**技巧 2: 追踪 TaskGroup 生命周期**
```python
class TrackedTaskGroup:
    async def __aenter__(self):
        print(f"[{time.time()}] TaskGroup entered")
        return await super().__aenter__()
    
    async def __aexit__(self, *args):
        print(f"[{time.time()}] TaskGroup exiting")
        result = await super().__aexit__(*args)
        print(f"[{time.time()}] TaskGroup exited")
        return result
```

---

**下一步**：阅读 [04-controller-layer.md](04-controller-layer.md) 了解控制器层设计

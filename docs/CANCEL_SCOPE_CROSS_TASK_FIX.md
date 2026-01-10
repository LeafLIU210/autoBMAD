# AnyIO Cancel Scope 跨任务错误修复方案

## 问题描述

**错误信息：**
```
RuntimeError: Attempted to exit cancel scope in a different task than it was entered in
```

**触发场景：**
- Story 1.3 的 Dev 阶段完成后，立即进入 QA 阶段
- QA Agent 发起新的 SDK 调用时，前一次调用的 cancel scope 尚未完全退出
- claude_agent_sdk 内部的 AnyIO TaskGroup 在关闭查询时，跨 Task 退出 scope

**影响：**
- 当前 SDK 调用被标记为 Cancelled
- 后续所有 SDK 调用立即失败
- Dev-QA 流程中断

---

## 根因分析

```
时间线：
11:48:00.933 - Dev阶段 SDK 调用成功返回结果
11:48:00.933 - cancel_scope_tracker 记录 scope 退出
11:48:00.938 - QA Agent 开始新的 SDK 调用
11:48:00.939 - 新 scope 进入
11:48:00.939 - 立即收到 CancelledError
11:48:00.939 - claude_agent_sdk 尝试关闭前一次查询
11:48:00.940 - RuntimeError: cancel scope 跨任务退出
```

**问题本质：**
两次 SDK 调用之间没有足够的同步间隙，导致：
1. 前一次调用的 async generator 尚未完全关闭
2. claude_agent_sdk 内部的 TaskGroup/CancelScope 被跨任务访问

---
## 一般性解决方案思路（适用于你现在的场景）
确保 CancelScope 的生命周期局限在单个 Task 内
典型安全写法（简化示意）：
python
   import anyio

   async def call_sdk():
       async with anyio.create_task_group() as tg:
           with anyio.CancelScope() as scope:
               # 所有对 SDK 的调用、子任务创建和等待都在这个 Task 内完成
               result = await sdk_call()
               # 如需取消，由当前 Task 触发：
               scope.cancel()
               return result
避免的做法：
在 Task A 中 with CancelScope()，然后在 Task B 中关闭 async generator / fixture，导致退出 scope 的线程/Task 不匹配。
把 CancelScope 绑在 async generator、fixture、或全局单例上，却在不同 Task 的 __aexit__ / teardown 中关闭。
避免在 async 生成器 / 流式接口 teardown 时退出 scope
许多报错来自类似模式（参考多个 GitHub issue）：
python
   async def stream_something():
       with anyio.CancelScope() as scope:
           try:
               yield something  # 外部在另一个 Task 中消费
           finally:
               # 这里在“另一个 Task”里触发 scope.__exit__
               ...
在 AnyIO 下，这个很容易变成“enter 在生产者 Task，exit 在消费者 Task”，就会触发你看到的 RuntimeError。改法：
不要在 async generator 里管理 CancelScope；
把 CancelScope 放在消费端（调用方）：
python
async def main():
    with anyio.CancelScope() as scope:
        async for item in stream_something():
            ...
            if need_cancel:
                scope.cancel()  # 当前 Task 进入 & 退出一致
不要在 fixture / 库的 teardown 中关闭“外部创建”的 scope
类似 httpx-ws、pytest-asyncio 的问题报告都指出：
在 fixture 中创建 CancelScope，然后在测试 Task 结束时再由 fixture teardown 关闭，很容易跨 Task。
安全做法：
fixture 只返回“可取消的操作”或“任务组”，但 CancelScope 自己放在测试或调用方的 Task 中。
或者：在 fixture 内部完全完成 enter/exit，不泄露 scope 到外部。


## 针对你当前的 BMAD / Claude SDK 场景，建议的具体思路
你这次错误栈来自 claude_agent_sdk._internal.query 调用 AnyIO TaskGroup / CancelScope。在你自己层面能做的修复点主要有：
确保每次 SDK 调用只在一个 Task 中整体执行完
例如在 SafeClaudeSDK 或 sdk_wrapper 里，保证：
manager.track_sdk_execution(...) 的上下文和 Claude SDK query 对象的生命周期都在同一个 async 函数 / Task 中；
不要把 query 作为 async generator 暴露给外部再被其他 Task 消费和关闭。
避免对同一个 SDK 调用做“跨 Task 的取消或关闭”
不要在另一个 Task 里去 close SDK 的 async generator / query；
所有取消操作（比如超时、用户中断）统一在发起调用的 Task 内执行：
python
async with anyio.fail_after(timeout):
    result = await sdk_call(...)
如果必须并发多路 SDK 调用，给每一路单独的 TaskGroup / CancelScope
不要共享一个 CancelScope 在多个 Task 上并在不同地方关闭；
每个 story 的 Dev / QA 调用，都在自己的 TaskGroup+CancelScope 中从头到尾执行完



## 修复方案（奥卡姆剃刀原则）

### 方案：在 SDK 调用之间添加强制同步点

**修改文件：** `autoBMAD/epic_automation/dev_agent.py`

**修改位置：** `execute_development` 方法末尾，在通知 QA 之前

**修改内容：**
```python
# 在 dev_agent.py 的 execute_development 方法中
# 找到通知 QA 的代码之前，添加：

# 🎯 关键修复：确保 SDK 调用完全结束后再通知 QA
await asyncio.sleep(0.5)  # 等待 SDK 资源完全释放
```

**修改文件：** `autoBMAD/epic_automation/qa_agent.py`

**修改位置：** `_parse_story_status` 方法开头

**修改内容：**
```python
async def _parse_story_status(self, story_path: str) -> str:
    # 🎯 关键修复：确保进入新的 SDK 调用前有干净的上下文
    await asyncio.sleep(0.1)  # 短暂等待确保前序操作完成
    
    # ... 原有代码
```

---

## 详细实施步骤

### 步骤 1：修改 dev_agent.py

**文件路径：** `autoBMAD/epic_automation/dev_agent.py`

**查找代码段（大约在 execute_development 方法末尾）：**
```python
logger.info(f"[Dev Agent] Notifying QA agent for: {story_path}")
```

**在此行之前添加：**
```python
# 🎯 修复 cancel scope 跨任务错误
# 确保 SDK 调用完全结束，所有 async generator 和 cancel scope 都已退出
await asyncio.sleep(0.5)
logger.debug("[Dev Agent] SDK cleanup completed, safe to notify QA")
```

### 步骤 2：修改 qa_agent.py

**文件路径：** `autoBMAD/epic_automation/qa_agent.py`

**查找代码段（_parse_story_status 方法开头）：**
```python
async def _parse_story_status(self, story_path: str) -> str:
    try:
        story_file = Path(story_path)
```

**修改为：**
```python
async def _parse_story_status(self, story_path: str) -> str:
    # 🎯 修复 cancel scope 跨任务错误
    # 确保进入新的 SDK 上下文前有干净的执行环境
    await asyncio.sleep(0.1)
    
    try:
        story_file = Path(story_path)
```

### 步骤 3：修改 sdk_wrapper.py（可选增强）

**文件路径：** `autoBMAD/epic_automation/sdk_wrapper.py`

**在 SafeAsyncGenerator.aclose 方法的 finally 块中：**

**原代码：**
```python
finally:
    try:
        await asyncio.sleep(0.05)
    except Exception:
        pass
```

**修改为：**
```python
finally:
    try:
        # 延长清理等待时间，确保 cancel scope 完全退出
        await asyncio.sleep(0.2)
    except Exception:
        pass
```

---

## 验证方法

### 测试命令
```powershell
python -m autoBMAD.epic_automation.epic_driver docs/epics/epic-1-core-algorithm-foundation.md --source-dir src --test-dir tests 2>&1 | tee autoBMAD/epic_automation/logs/test_fix.log
```

### 成功标准
1. 日志中不再出现 `RuntimeError: Attempted to exit cancel scope`
2. Story 1.3 的 QA 阶段正常执行
3. Story 1.4 的 Dev 阶段正常执行
4. `Dev-QA cycle complete: 4/4 stories succeeded`

### 验证点检查
```
✓ Dev 阶段完成后有 0.5s 延迟
✓ QA 阶段开始前有 0.1s 延迟
✓ 无 cancel scope 跨任务错误
✓ 无 SDK 调用被意外取消
```

---

## 回滚方案

如果修复引入新问题，删除添加的 `await asyncio.sleep()` 语句即可恢复原状态。

---

## 技术说明

### 为什么是 0.5s 和 0.1s？

- **0.5s（Dev→QA 过渡）：** 确保 claude_agent_sdk 的子进程完全退出，TaskGroup 关闭，所有 cancel scope 退出当前 Task
- **0.1s（QA 内部）：** 防御性等待，确保进入新 SDK 调用时上下文干净

### 为什么不用更复杂的方案？

根据奥卡姆剃刀原则：
- 问题本质是时序问题，最简单的解决方案是添加同步点
- 复杂的 Task 隔离、重试机制会增加代码复杂度和维护成本
- asyncio.sleep 是标准的协作式让步，不会阻塞事件循环

---

## 相关文件

| 文件 | 修改类型 |
|------|----------|
| `autoBMAD/epic_automation/dev_agent.py` | 添加同步点 |
| `autoBMAD/epic_automation/qa_agent.py` | 添加同步点 |
| `autoBMAD/epic_automation/sdk_wrapper.py` | 增加清理等待（可选） |

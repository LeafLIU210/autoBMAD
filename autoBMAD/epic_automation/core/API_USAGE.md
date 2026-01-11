# SDK执行层 API 使用文档

## 概述

本文档介绍如何使用 SDK 执行层的核心组件。

**当前状态**: Day 1 完成
- ✅ SDKResult - 完整实现
- ✅ CancellationManager - 完整实现
- ✅ SDKExecutor - 骨架实现
- ⚠️ SafeClaudeSDK - 骨架实现（Day 3 完整）

---

## 1. SDKResult

### 1.1 基本用法

```python
from autoBMAD.epic_automation.core import SDKResult, SDKErrorType

# 创建成功结果
result = SDKResult(
    has_target_result=True,
    cleanup_completed=True,
    session_id="session-123",
    agent_name="TestAgent"
)

# 检查业务是否成功
if result.is_success():
    print("业务执行成功!")
    print(f"会话: {result.session_id}")
    print(f"Agent: {result.agent_name}")
    print(f"耗时: {result.duration_seconds:.2f}s")

# 访问结果数据
messages = result.messages
target_message = result.target_message
```

### 1.2 错误处理

```python
# 创建失败结果
result = SDKResult(
    has_target_result=False,
    cleanup_completed=False,
    error_type=SDKErrorType.CANCELLED,
    errors=["用户取消了操作"],
    last_exception=ValueError("取消原因")
)

# 检查失败原因
if result.is_cancelled():
    print("操作被取消")

if result.is_timeout():
    print("操作超时")

if result.has_cancel_scope_error():
    print("Cancel Scope错误")

# 获取错误摘要
print(result.get_error_summary())
```

### 1.3 完整示例

```python
from autoBMAD.epic_automation.core import SDKResult, SDKErrorType

def process_sdk_result(result: SDKResult) -> None:
    """处理SDK执行结果"""
    print(f"\n{'='*50}")
    print(f"会话: {result.session_id}")
    print(f"Agent: {result.agent_name}")
    print(f"状态: {result}")
    print(f"{'='*50}\n")

    if result.is_success():
        print("✅ 业务成功")
        print(f"   目标消息: {result.target_message}")
        print(f"   消息数量: {len(result.messages)}")
    else:
        print("❌ 业务失败")
        print(f"   错误类型: {result.error_type.value}")
        print(f"   错误信息: {result.get_error_summary()}")
        if result.last_exception:
            print(f"   异常: {result.last_exception}")
```

---

## 2. CancellationManager

### 2.1 基本用法

```python
from autoBMAD.epic_automation.core import CancellationManager
import asyncio

async def example_usage():
    """CancellationManager 使用示例"""
    manager = CancellationManager()

    # 1. 注册SDK调用
    call_id = "sdk-call-123"
    agent_name = "TestAgent"
    manager.register_call(call_id, agent_name)

    # 2. 模拟SDK执行过程
    # ... SDK执行中 ...

    # 3. 请求取消
    manager.request_cancel(call_id)

    # 4. 完成清理
    manager.mark_cleanup_completed(call_id)

    # 5. 验证可以安全进行下一步
    safe = await manager.confirm_safe_to_proceed(call_id, timeout=5.0)
    if safe:
        print("✅ 可以安全进行下一步")
    else:
        print("❌ 等待清理完成超时")

    # 6. 注销调用
    manager.unregister_call(call_id)
```

### 2.2 双条件验证机制

```python
import asyncio
from autoBMAD.epic_automation.core import CancellationManager

async def test_double_condition():
    """测试双条件验证机制"""
    manager = CancellationManager()
    call_id = "test-call"

    # 注册调用
    manager.register_call(call_id, "TestAgent")

    # 测试场景1: 只有取消请求，没有清理完成
    manager.request_cancel(call_id)
    safe = await manager.confirm_safe_to_proceed(call_id, timeout=0.5)
    print(f"场景1 (只有取消): {safe}")  # False

    # 恢复状态
    manager.unregister_call(call_id)
    manager.register_call(call_id, "TestAgent")

    # 测试场景2: 只有清理完成，没有取消请求
    manager.mark_cleanup_completed(call_id)
    safe = await manager.confirm_safe_to_proceed(call_id, timeout=0.5)
    print(f"场景2 (只有清理): {safe}")  # False

    # 恢复状态
    manager.unregister_call(call_id)
    manager.register_call(call_id, "TestAgent")

    # 测试场景3: 两个条件都满足
    manager.request_cancel(call_id)
    manager.mark_cleanup_completed(call_id)
    safe = await manager.confirm_safe_to_proceed(call_id, timeout=0.5)
    print(f"场景3 (都满足): {safe}")  # True
```

### 2.3 完整示例

```python
import asyncio
from autoBMAD.epic_automation.core import CancellationManager

class SDKCallTracker:
    """SDK调用跟踪器"""
    def __init__(self):
        self.manager = CancellationManager()

    async def execute_sdk_call(self, call_id: str, agent_name: str):
        """执行SDK调用"""
        try:
            # 注册调用
            self.manager.register_call(call_id, agent_name)
            print(f"[{agent_name}] 开始执行: {call_id}")

            # 模拟SDK执行
            await asyncio.sleep(0.5)

            # 找到目标结果
            self.manager.mark_target_result_found(call_id)
            print(f"[{agent_name}] 找到目标结果: {call_id}")

            # 请求取消
            self.manager.request_cancel(call_id)

            # 执行清理
            await asyncio.sleep(0.3)
            self.manager.mark_cleanup_completed(call_id)
            print(f"[{agent_name}] 清理完成: {call_id}")

            # 验证可以安全进行
            safe = await self.manager.confirm_safe_to_proceed(call_id, timeout=2.0)
            if safe:
                print(f"[{agent_name}] 可以安全进行下一步: {call_id}")
            else:
                print(f"[{agent_name}] 等待清理超时: {call_id}")

        finally:
            # 注销调用
            self.manager.unregister_call(call_id)

# 使用示例
async def main():
    tracker = SDKCallTracker()
    await tracker.execute_sdk_call("call-1", "TestAgent")

asyncio.run(main())
```

---

## 3. SDKExecutor (骨架)

### 3.1 当前状态

SDKExecutor 目前处于骨架实现阶段：

```python
from autoBMAD.epic_automation.core import SDKExecutor
import asyncio

async def example():
    """当前可用功能"""
    executor = SDKExecutor()

    # 1. 验证初始化
    assert executor.cancel_manager is not None
    print("✅ SDKExecutor 初始化成功")

    # 2. 验证异常处理
    async def mock_sdk():
        yield {"type": "message"}

    def target_predicate(msg):
        return False

    # 当前实现会抛出NotImplementedError，但被正确捕获
    result = await executor.execute(
        sdk_func=mock_sdk,
        target_predicate=target_predicate,
        agent_name="TestAgent"
    )

    # 验证异常被封装到SDKResult中
    assert result.error_type == SDKErrorType.UNKNOWN
    print("✅ 异常处理机制正常")

# 运行示例
asyncio.run(example())
```

### 3.2 Day 2 完整实现后

Day 2 完成后，使用方式将如下：

```python
from autoBMAD.epic_automation.core import SDKExecutor
import asyncio

async def example_complete():
    """完整实现后的使用方式"""
    executor = SDKExecutor()

    # 定义SDK调用
    async def sdk_func():
        yield {"type": "message", "content": "开始"}
        yield {"type": "message", "content": "处理中"}
        yield {"type": "result", "content": "完成"}
        yield {"type": "cleanup", "content": "清理"}

    # 定义目标检测
    def target_predicate(msg):
        return msg.get("type") == "result"

    # 执行SDK调用
    result = await executor.execute(
        sdk_func=sdk_func,
        target_predicate=target_predicate,
        timeout=30.0,
        agent_name="TestAgent"
    )

    # 处理结果
    if result.is_success():
        print(f"✅ 成功: {result.target_message}")
    else:
        print(f"❌ 失败: {result.get_error_summary()}")

asyncio.run(example_complete())
```

---

## 4. SafeClaudeSDK (骨架)

### 4.1 当前状态

SafeClaudeSDK 目前处于骨架实现阶段：

```python
from autoBMAD.epic_automation.core import SafeClaudeSDK

# 检查SDK可用性
if SafeClaudeSDK.is_sdk_available():
    print("✅ Claude SDK 可用")
else:
    print("❌ Claude SDK 不可用")

# 创建实例（需要SDK可用）
try:
    sdk = SafeClaudeSDK(
        prompt="你好",
        options=None,  # 将使用默认选项
        log_manager=None
    )
    print("✅ SafeClaudeSDK 创建成功")
except RuntimeError as e:
    print(f"❌ 创建失败: {e}")
```

### 4.2 Day 3 完整实现后

```python
from autoBMAD.epic_automation.core import SafeClaudeSDK
import asyncio

async def example_complete():
    """完整实现后的使用方式"""
    # 创建SDK实例
    sdk = SafeClaudeSDK(prompt="说 'Hello World'")

    # 使用异步生成器
    async for message in sdk.execute():
        print(f"收到消息: {message}")

asyncio.run(example_complete())
```

---

## 5. 完整集成示例

### 5.1 当前可运行示例

```python
"""当前可运行的功能演示"""
import asyncio
from autoBMAD.epic_automation.core import (
    SDKResult, SDKErrorType,
    CancellationManager,
    SDKExecutor
)

async def demo_current_features():
    """演示当前可用的功能"""
    print("=" * 60)
    print("SDK执行层 - 当前可用功能演示")
    print("=" * 60)

    # 1. SDKResult 使用
    print("\n1. SDKResult 使用:")
    result = SDKResult(
        has_target_result=True,
        cleanup_completed=True,
        session_id="demo-session",
        agent_name="DemoAgent"
    )
    print(f"   {result}")

    # 2. CancellationManager 使用
    print("\n2. CancellationManager 使用:")
    manager = CancellationManager()
    manager.register_call("call-1", "DemoAgent")
    manager.request_cancel("call-1")
    manager.mark_cleanup_completed("call-1")
    safe = await manager.confirm_safe_to_proceed("call-1")
    print(f"   双条件验证结果: {safe}")
    manager.unregister_call("call-1")

    # 3. SDKExecutor 初始化
    print("\n3. SDKExecutor 初始化:")
    executor = SDKExecutor()
    print(f"   初始化成功: {executor.cancel_manager is not None}")

    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)

# 运行演示
if __name__ == "__main__":
    asyncio.run(demo_current_features())
```

### 5.2 完整实现后的集成示例

```python
"""完整实现后的集成示例"""
import asyncio
from autoBMAD.epic_automation.core import (
    SDKExecutor,
    SafeClaudeSDK
)

async def demo_complete_integration():
    """完整集成演示"""
    executor = SDKExecutor()

    async def sdk_func():
        sdk = SafeClaudeSDK(prompt="说 'Hello World'")
        async for message in sdk.execute():
            yield message

    def target_predicate(msg):
        return "World" in str(msg)

    result = await executor.execute(
        sdk_func=sdk_func,
        target_predicate=target_predicate,
        agent_name="ClaudeAgent"
    )

    if result.is_success():
        print(f"✅ 执行成功: {result.target_message}")
    else:
        print(f"❌ 执行失败: {result.get_error_summary()}")

# 运行完整演示
asyncio.run(demo_complete_integration())
```

---

## 6. 错误处理指南

### 6.1 常见错误类型

```python
from autoBMAD.epic_automation.core import SDKErrorType

# 处理不同错误类型
def handle_sdk_result(result: SDKResult):
    """根据错误类型处理结果"""
    if result.is_success():
        # 成功处理
        return result.target_message

    elif result.is_cancelled():
        # 被取消 - 这是正常情况，不是错误
        print("操作被取消（正常情况）")
        return None

    elif result.is_timeout():
        # 超时 - 可以重试
        print("操作超时，建议重试")
        return None

    elif result.has_cancel_scope_error():
        # Cancel Scope 错误 - 这是关键问题
        print("❌ Cancel Scope 错误（需要修复）")
        raise RuntimeError("Cancel Scope 错误")

    elif result.has_sdk_error():
        # SDK 内部错误
        print("❌ SDK 内部错误")
        return None

    else:
        # 未知错误
        print("❌ 未知错误")
        return None
```

### 6.2 最佳实践

```python
# 1. 总是检查 is_success()
result = await executor.execute(...)
if not result.is_success():
    # 处理失败
    handle_failure(result)

# 2. 记录完整的错误信息
if not result.is_success():
    logger.error(
        f"SDK调用失败: {result.session_id}, "
        f"错误: {result.get_error_summary()}"
    )
    if result.last_exception:
        logger.exception("异常详情", exc_info=result.last_exception)

# 3. 双条件验证机制确保资源清理
# CancellationManager 自动处理
```

---

## 7. API 参考

### 7.1 SDKResult

| 方法 | 描述 | 返回值 |
|------|------|--------|
| `is_success()` | 业务是否成功 | `bool` |
| `is_cancelled()` | 是否被取消 | `bool` |
| `is_timeout()` | 是否超时 | `bool` |
| `has_cancel_scope_error()` | 是否有Cancel Scope错误 | `bool` |
| `has_sdk_error()` | 是否有SDK错误 | `bool` |
| `get_error_summary()` | 获取错误摘要 | `str` |
| `__str__()` | 字符串表示 | `str` |

### 7.2 CancellationManager

| 方法 | 描述 | 参数 |
|------|------|------|
| `register_call()` | 注册SDK调用 | `call_id: str, agent_name: str` |
| `request_cancel()` | 请求取消 | `call_id: str` |
| `mark_cleanup_completed()` | 标记清理完成 | `call_id: str` |
| `mark_target_result_found()` | 标记找到目标结果 | `call_id: str` |
| `confirm_safe_to_proceed()` | 确认可以安全进行 | `call_id: str, timeout: float` |
| `unregister_call()` | 注销调用 | `call_id: str` |
| `get_active_calls_count()` | 获取活跃调用数 | - |

### 7.3 SDKExecutor

| 方法 | 描述 | 参数 |
|------|------|------|
| `execute()` | 执行SDK调用 | `sdk_func, target_predicate, timeout, agent_name` |

### 7.4 SafeClaudeSDK

| 方法 | 描述 | 参数 |
|------|------|------|
| `is_sdk_available()` | 检查SDK可用性 | - |
| `execute()` | 执行SDK调用 | - |

---

## 8. 迁移指南

### 8.1 从旧架构迁移

旧代码：
```python
# 旧方式 - 直接调用SDK
result = await query(prompt, options)
```

新代码：
```python
# 新方式 - 使用SDKExecutor
executor = SDKExecutor()
async def sdk_func():
    sdk = SafeClaudeSDK(prompt)
    async for msg in sdk.execute():
        yield msg

result = await executor.execute(
    sdk_func=sdk_func,
    target_predicate=lambda x: x.type == "result"
)
```

### 8.2 优势对比

| 方面 | 旧架构 | 新架构 |
|------|--------|--------|
| Cancel Scope | ❌ 跨Task错误 | ✅ 完全隔离 |
| 错误处理 | ❌ 异常传播 | ✅ 统一封装 |
| 资源清理 | ❌ 手动管理 | ✅ 自动清理 |
| 状态管理 | ❌ 分散 | ✅ 统一SDKResult |
| 测试性 | ❌ 困难 | ✅ 简单 |

---

## 9. 故障排查

### 9.1 常见问题

**Q: 如何调试Cancel Scope错误？**
```python
# 检查是否有Cancel Scope错误
if result.has_cancel_scope_error():
    logger.error("Cancel Scope错误")
    logger.error(f"会话: {result.session_id}")
    logger.error(f"错误: {result.get_error_summary()}")
```

**Q: 如何验证双条件验证机制？**
```python
# 手动验证
info = manager.get_call_info(call_id)
print(f"取消请求: {info.cancel_requested}")
print(f"清理完成: {info.cleanup_completed}")
print(f"安全进行: {info.cancel_requested and info.cleanup_completed}")
```

**Q: 如何查看所有活跃调用？**
```python
count = manager.get_active_calls_count()
print(f"活跃调用数: {count}")

# 遍历所有调用
for call_id, info in manager._active_calls.items():
    print(f"调用: {info.call_id}, Agent: {info.agent_name}")
```

---

## 10. 下一步

### 10.1 Day 2 任务

- [ ] 实现流式消息收集
- [ ] 实现目标检测逻辑
- [ ] 实现取消机制
- [ ] 集成测试

### 10.2 Day 3 任务

- [ ] 完整实现SafeClaudeSDK
- [ ] E2E测试
- [ ] TaskGroup隔离验证

---

**文档版本**: 1.0
**最后更新**: 2026-01-11
**状态**: Day 1 完成

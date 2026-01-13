# 质量门控 Cancel Scope 错误修复方案

**问题**: Quality Gates (RuffAgent) 在 SDK 调用后出现 `RuntimeError: Attempted to exit cancel scope in a different task than it was entered in`

**状态**: 待实施  
**优先级**: P1 - 高优先级  
**创建时间**: 2026-01-10

---

## 问题定位

### 错误现象

```
2026-01-10 14:09:50,396 - autoBMAD.epic_automation.quality_agents - INFO - Generated fixes for 3 issues
2026-01-10 14:09:50,397 - claude_agent_sdk._internal.query - DEBUG - Read task cancelled
2026-01-10 14:09:50,397 - asyncio - ERROR - Task exception was never retrieved
future: <Task finished name='Task-6' coro=<<async_generator_athrow without __name__>()> 
  exception=RuntimeError('Attempted to exit cancel scope in a different task than it was entered in')>
```

### 根因分析

1. **触发点**: Quality Gates 的 `CodeQualityAgent.fix_issues()` 直接使用 `claude_agent_sdk.query()`
2. **根本原因**: 没有走 `SafeClaudeSDK` + `SDKCancellationManager` 的已修复结构
3. **技术细节**: claude_agent_sdk 内部 TaskGroup/CancelScope 在不同 Task 中 enter/exit
4. **影响范围**: 修复功能正常完成，但会产生错误日志，影响监控和调试

---

## 修复方案

### 方案 1: 统一使用 SafeClaudeSDK（主方案）

**目标**: 让质量门控的 SDK 调用复用 `SafeClaudeSDK` 已实现的跨 Task 防护机制

#### 1.1 修改范围

**文件**: `autoBMAD/epic_automation/quality_agents.py`

**修改点**:
- `CodeQualityAgent.fix_issues()` 方法
- 移除直接使用 `_query` 的代码
- 改用 `SafeClaudeSDK` 封装

#### 1.2 实施步骤

**步骤 1**: 在 `quality_agents.py` 顶部导入 SafeClaudeSDK

```python
from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK, SDK_AVAILABLE
```

**步骤 2**: 重构 `fix_issues()` 方法的 SDK 调用部分

替换现有的:
```python
response_iterator = _query(prompt=prompt, options=options)
async for message in response_iterator:
    ...
```

改为:
```python
# 使用 SafeClaudeSDK 封装，自动处理 Cancel Scope 跨 Task 问题
sdk = SafeClaudeSDK(
    prompt=prompt,
    options=options,
    timeout=None,
    log_manager=None
)

success = await sdk.execute()
if success:
    # SDK 执行成功
    fixed_count = len(issues)
    return True, f"Successfully generated fixes for {fixed_count} issues", fixed_count
else:
    return False, "SDK execution failed", 0
```

**步骤 3**: 简化 `_run_sdk_call()` 内部逻辑

- 移除复杂的消息迭代和 ResultMessage 判断
- 依赖 `SafeClaudeSDK.execute()` 的布尔返回值
- 减少 CancelledError 的手动处理（SafeClaudeSDK 已内置）

**步骤 4**: 移除外层 `asyncio.shield` 和 `create_task` 隔离

- SafeClaudeSDK 内部已有 TaskGroup 和 CancelScope 隔离
- 不需要在外层重复防护

#### 1.3 预期效果

- ✅ 质量门控 SDK 调用与 Dev/QA 流程使用统一防护机制
- ✅ 消除 "Attempted to exit cancel scope in a different task" 错误
- ✅ 代码复用度提高，维护成本降低
- ✅ 日志输出更清晰（复用 SDKMessageTracker）

---

### 方案 2: RuntimeError 容错机制（辅助方案）

**目标**: 确保所有 RuntimeError（包括 cancel scope 错误）不会中止工作流

#### 2.1 修改范围

**文件**: `autoBMAD/epic_automation/quality_agents.py`

**修改点**:
- `CodeQualityAgent.fix_issues()` 的异常处理
- `CodeQualityAgent.retry_cycle()` 的错误恢复

#### 2.2 实施步骤

**步骤 1**: 在 `fix_issues()` 中增强 RuntimeError 捕获

```python
async def fix_issues(...) -> tuple[bool, str, int]:
    try:
        # SDK 调用逻辑
        ...
    except RuntimeError as e:
        error_msg = str(e)
        if "cancel scope" in error_msg.lower():
            # Cancel Scope 错误：功能可能已完成，记录警告但不中止
            logger.warning(
                f"RuntimeError during SDK cleanup (non-fatal): {error_msg}"
            )
            # 返回失败状态，允许重试机制介入
            return False, "SDK cleanup error (will retry)", 0
        else:
            # 其他 RuntimeError：记录但不抛出
            logger.error(f"RuntimeError during fix: {error_msg}")
            return False, f"Runtime error: {error_msg}", 0
    except Exception as e:
        # 所有其他异常也不中止流程
        logger.error(f"Error generating fixes: {e}")
        return False, f"Error generating fixes: {str(e)}", 0
```

**步骤 2**: 在 `retry_cycle()` 中确保循环不中断

```python
async def retry_cycle(...) -> dict[str, Any]:
    for cycle_num in range(1, max_cycles + 1):
        try:
            # 执行检查
            success, issues = await self.execute_check(source_dir)
            ...
            
            # 执行修复
            for retry_num in range(1, retries_per_cycle + 1):
                try:
                    fix_success, fix_message, fixed_count = await self.fix_issues(...)
                    ...
                except Exception as e:
                    # 捕获所有异常，记录后继续重试
                    logger.error(f"Exception in retry {retry_num}: {e}")
                    if retry_num >= retries_per_cycle:
                        # 最后一次重试失败，标记为失败但继续下一个周期
                        fix_success = False
                        fix_message = f"Max retries failed: {e}"
                        fixed_count = 0
                    continue
                    
        except Exception as e:
            # 周期级别的异常也不中止整个流程
            logger.error(f"Exception in cycle {cycle_num}: {e}")
            cycle_results["cycles"].append({
                "cycle": cycle_num,
                "success": False,
                "issues_found": 0,
                "issues_fixed": 0,
                "error": f"Cycle exception: {e}"
            })
            continue
    
    return cycle_results
```

**步骤 3**: 在 `QualityGateOrchestrator` 中添加全局异常处理

```python
async def run_ruff_gate(self, source_dir: Path) -> dict[str, Any]:
    try:
        result = await self.ruff_agent.retry_cycle(source_dir)
        return result
    except Exception as e:
        # 即使质量门控完全失败，也返回结构化结果而非抛异常
        logger.error(f"Ruff gate failed with exception: {e}")
        return {
            "total_cycles": 0,
            "successful_cycles": 0,
            "total_issues_found": 0,
            "total_issues_fixed": 0,
            "cycles": [],
            "error": str(e),
            "status": "failed_with_exception"
        }
```

#### 2.3 预期效果

- ✅ 任何 RuntimeError 不会中止质量门控流程
- ✅ 重试机制可以自动恢复临时性错误
- ✅ 完整的错误日志便于事后分析
- ✅ 工作流稳定性显著提升

---

## 实施计划

### Phase 1: 主修复（方案 1）

**时间**: 1-2 小时  
**优先级**: P0

1. 修改 `quality_agents.py` 导入 SafeClaudeSDK
2. 重构 `fix_issues()` 方法使用 SafeClaudeSDK
3. 简化异常处理逻辑
4. 本地测试：运行完整 Epic 1

### Phase 2: 容错增强（方案 2）

**时间**: 30 分钟  
**优先级**: P1

1. 在 `fix_issues()` 增强 RuntimeError 处理
2. 在 `retry_cycle()` 添加周期级异常保护
3. 在 Orchestrator 添加全局异常捕获
4. 测试验证：模拟各类异常场景

### Phase 3: 验证与监控

**时间**: 30 分钟  
**优先级**: P1

1. 运行完整 Epic 1，确认无 cancel scope 错误
2. 检查日志，确认所有 SDK 调用都走 SafeClaudeSDK
3. 验证异常场景下流程不中断
4. 更新 `CANCEL_SCOPE_FIX_PROGRESS.md` 状态

---

## 验证标准

### 功能验证

- [ ] 运行 Epic 1 完整流程，质量门控成功执行
- [ ] 日志中无 "Attempted to exit cancel scope" 错误
- [ ] Ruff 检查和修复功能正常工作
- [ ] 所有 SDK 调用都有 SafeClaudeSDK 的特征日志

### 异常验证

- [ ] 模拟 SDK 超时，流程不中断
- [ ] 模拟 cancel scope 错误，重试机制生效
- [ ] 模拟网络错误，异常被正确记录
- [ ] 质量门控失败时返回结构化错误信息

### 性能验证

- [ ] 质量门控执行时间无显著增加
- [ ] 内存使用无异常增长
- [ ] 日志大小在可接受范围内

---

## 回滚方案

如果修复引入新问题：

1. 回滚 `quality_agents.py` 到当前版本
2. 保留方案 2 的容错机制（风险低）
3. 采用临时方案：自定义 asyncio exception handler 降噪

```python
# 临时降噪方案（在 epic_driver.py 初始化时执行）
import asyncio
import logging

def suppress_cancel_scope_error(loop, context):
    exc = context.get("exception")
    if isinstance(exc, RuntimeError) and "cancel scope" in str(exc).lower():
        logger.debug("Suppressed cancel scope error in SDK cleanup", exc_info=exc)
        return
    loop.default_exception_handler(context)

loop = asyncio.get_event_loop()
loop.set_exception_handler(suppress_cancel_scope_error)
```

---

## 附录

### 相关文档

- `CANCEL_SCOPE_CROSS_TASK_SOLUTION.md` - 原始问题分析
- `CANCEL_SCOPE_FIX_IMPLEMENTATION_REPORT.md` - Dev/QA 修复报告
- `sdk_wrapper.py` - SafeClaudeSDK 实现

### 参考 Issue

- GitHub: modelcontextprotocol/python-sdk#252
- GitHub: anthropics/claude-agent-sdk-python#378
- GitHub: lastmile-ai/mcp-agent#35

### 技术要点

- AnyIO CancelScope 必须在同一 Task 中 enter/exit
- async generator cleanup 可能在不同 Task 上触发
- SafeClaudeSDK 使用 TaskGroup 确保生命周期一致性
- SDKCancellationManager 统一追踪所有 SDK 调用状态

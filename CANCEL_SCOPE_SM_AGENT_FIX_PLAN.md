# Cancel Scope 错误修复方案 - SM Agent 路径

**问题报告**: 2026-01-10 18:15:45  
**修复优先级**: P0 - 阻塞性问题  
**影响范围**: Epic Driver → SM Agent → Claude SDK 调用链路

---

## 一、问题定位

### 1.1 错误现象

```
2026-01-10 18:17:52,461 - autoBMAD.epic_automation.sdk_wrapper - ERROR - Claude SDK execution failed: 
Attempted to exit a cancel scope that isn't the current tasks's current cancel scope
```

### 1.2 发生时机

- **功能层面**: SM Agent 成功创建 4 个 story 文件，功能已完成
- **错误层面**: Claude SDK 在收尾清理阶段（async generator cleanup）抛出 RuntimeError
- **影响**: SafeClaudeSDK 标记本次调用失败（返回 False），Epic Driver 认为 story 创建失败

### 1.3 根本原因

claude_agent_sdk 内部使用 AnyIO 的 CancelScope/TaskGroup：
- CancelScope 在 Task A 中 enter
- 在异步生成器清理或 TaskGroup 内的其他 task 上 exit
- AnyIO 检测到跨任务退出，抛出 RuntimeError

---

## 二、修复策略

### 2.1 核心原则

> 保持 CancelScope/TaskGroup 生命周期完全受 SafeClaudeSDK + SDKCancellationManager 控制，所有 Agent 只通过这两个组件发起 SDK 调用；每次调用后必须等待取消与清理完全完成（wait + confirm），连续调用之间留足 0.5s，同步地捕获并降级处理所有 RuntimeError（尤其 cancel scope 错误），保证 Epic 整体工作流不会因清理阶段的跨任务异常中断。

### 2.2 三层防护架构

```
┌─────────────────────────────────────────────────────────┐
│ Layer 3: Epic Driver / Agent 层                         │
│ - 捕获所有 RuntimeError（非致命处理）                   │
│ - 连续 SDK 调用间隔 0.5s                                │
│ - 单个 story 失败不中断整体流程                         │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 2: SDKCancellationManager                         │
│ - wait_for_cancellation_complete(timeout=5.0)           │
│ - confirm_safe_to_proceed() 双条件验证                  │
│ - detect_cross_task_risk() 风险检测                     │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 1: SafeClaudeSDK                                  │
│ - TaskGroup + CancelScope 隔离                          │
│ - track_sdk_execution 统一追踪                          │
│ - _rebuild_execution_context 重试恢复                   │
└─────────────────────────────────────────────────────────┘
```

---

## 三、具体修复方案

### 方案 1: SafeClaudeSDK 错误语义优化【关键】

#### 目标
将 SDK 清理阶段的 cancel scope RuntimeError 视为「功能完成但清理有噪声」，而非完全失败。

#### 实施位置
`autoBMAD/epic_automation/sdk_wrapper.py`

#### 修改点 1.1: execute() 方法增加清理错误容忍逻辑

```python
async def execute(self) -> bool:
    """
    执行 Claude SDK 查询
    
    🎯 增强：清理阶段的 cancel scope 错误不视为完全失败
    """
    if not SDK_AVAILABLE:
        logger.warning("Claude Agent SDK not available")
        return False

    max_retries = 2
    retry_count = 0
    
    # 🎯 新增：追踪是否已收到有效结果
    result_received = False

    while retry_count <= max_retries:
        try:
            success = await self._execute_with_recovery()
            
            # 如果成功，标记已收到结果
            if success:
                result_received = True
            
            return success
            
        except RuntimeError as e:
            error_msg = str(e)
            
            # 🎯 关键判断：cancel scope 错误 + 已收到结果 → 视为成功
            if "cancel scope" in error_msg and "different task" in error_msg:
                if result_received or self.message_tracker.has_valid_result():
                    logger.warning(
                        f"[SafeClaudeSDK] Cancel scope error in cleanup phase, "
                        f"but SDK already returned valid result. Treating as success."
                    )
                    return True
                
                # 否则正常重试
                retry_count += 1
                logger.warning(
                    f"[SafeClaudeSDK] Cancel scope cross-task error detected "
                    f"(attempt {retry_count}/{max_retries+1}). Rebuilding context..."
                )
                
                if retry_count > max_retries:
                    logger.error(
                        "[SafeClaudeSDK] Max retries reached for cancel scope error."
                    )
                    raise
                
                await self._rebuild_execution_context()
                continue
            else:
                raise
                
        except Exception:
            raise

    return False
```

#### 修改点 1.2: SDKMessageTracker 增加结果有效性判断

```python
class SDKMessageTracker:
    """SDK 消息追踪器"""
    
    def __init__(self, log_manager: Any | None = None):
        self.messages: list[str] = []
        self.log_manager = log_manager
        self.has_assistant_response = False  # 新增
        self.has_success_result = False      # 新增
    
    def track_message(self, msg_type: str, content: str | None):
        """追踪消息"""
        if content:
            self.messages.append(f"[{msg_type}] {content}")
            
            # 🎯 新增：标记有效响应
            if msg_type == "ASSISTANT":
                self.has_assistant_response = True
            elif msg_type == "SUCCESS":
                self.has_success_result = True
            
            if self.log_manager:
                self.log_manager.log(content, msg_type)
    
    def has_valid_result(self) -> bool:
        """
        判断是否已收到有效结果
        
        条件：有 ASSISTANT 消息或 SUCCESS 消息
        """
        return self.has_assistant_response or self.has_success_result
```

---

### 方案 2: SM Agent 增强错误处理【必须】

#### 目标
在 Agent 层捕获并降级处理 RuntimeError，不中断 Epic 流程。

#### 实施位置
`autoBMAD/epic_automation/sm_agent.py`

#### 修改点 2.1: create_stories() 方法增加 RuntimeError 处理

```python
async def create_stories(self, epic_path: Path) -> bool:
    """
    从 Epic 创建 Stories
    
    🎯 增强：RuntimeError 非致命处理
    """
    try:
        # ... 现有逻辑 ...
        
        sdk = SafeClaudeSDK(
            prompt=prompt,
            options=options,
            timeout=None,
            log_manager=self.log_manager
        )
        
        success = await sdk.execute()
        
        if success:
            self.logger.info("[SM Agent] Stories created successfully")
            return True
        else:
            self.logger.warning("[SM Agent] SDK execution returned False")
            return False
    
    except RuntimeError as e:
        error_msg = str(e)
        
        # 🎯 关键：cancel scope 错误特殊处理
        if "cancel scope" in error_msg.lower():
            self.logger.warning(
                f"[SM Agent] RuntimeError during SDK cleanup (non-fatal): {error_msg}"
            )
            
            # 检查 story 文件是否已创建成功
            if self._verify_stories_created(story_ids):
                self.logger.info(
                    "[SM Agent] Stories verified on disk despite cleanup error. "
                    "Treating as success."
                )
                return True
            else:
                self.logger.warning(
                    "[SM Agent] Stories not found on disk. Will retry if allowed."
                )
                return False
        else:
            # 其他 RuntimeError
            self.logger.error(f"[SM Agent] RuntimeError: {error_msg}")
            return False
    
    except Exception as e:
        self.logger.error(f"[SM Agent] Exception during story creation: {e}")
        return False

def _verify_stories_created(self, story_ids: list[str]) -> bool:
    """
    验证 story 文件是否已创建
    
    Args:
        story_ids: Story ID 列表
    
    Returns:
        True if all stories exist on disk
    """
    stories_dir = Path("docs/stories")
    
    for story_id in story_ids:
        story_file = stories_dir / f"{story_id}.md"
        if not story_file.exists():
            self.logger.debug(f"Story file not found: {story_file}")
            return False
    
    self.logger.debug(f"All {len(story_ids)} story files verified on disk")
    return True
```

---

### 方案 3: Epic Driver 增加连续调用间隔【必须】

#### 目标
在连续 SDK 调用之间留足资源清理时间。

#### 实施位置
`autoBMAD/epic_automation/epic_driver.py`

#### 修改点 3.1: 主循环增加清理间隔

```python
async def process_epic(self, epic_path: Path) -> dict:
    """
    处理 Epic
    
    🎯 增强：连续 SDK 调用间隔控制
    """
    stories = self._parse_epic(epic_path)
    
    results = []
    
    for idx, story in enumerate(stories):
        self.logger.info(f"Processing story {idx+1}/{len(stories)}: {story['id']}")
        
        try:
            # SM Phase
            if story['status'] != 'ready':
                sm_success = await self.sm_agent.create_story(story['id'])
                
                # 🎯 关键：SM 调用完成后等待清理
                await asyncio.sleep(0.5)
                
                if not sm_success:
                    self.logger.warning(f"SM phase failed for {story['id']}")
                    results.append({'id': story['id'], 'status': 'sm_failed'})
                    continue
            
            # Dev Phase
            dev_success = await self.dev_agent.execute(story['path'])
            
            # 🎯 关键：Dev 调用完成后等待清理
            await asyncio.sleep(0.5)
            
            if not dev_success:
                self.logger.warning(f"Dev phase failed for {story['id']}")
                results.append({'id': story['id'], 'status': 'dev_failed'})
                continue
            
            # QA Phase
            qa_success = await self.qa_agent.validate(story['path'])
            
            # 🎯 关键：QA 调用完成后等待清理
            await asyncio.sleep(0.5)
            
            if qa_success:
                results.append({'id': story['id'], 'status': 'completed'})
            else:
                results.append({'id': story['id'], 'status': 'qa_failed'})
        
        except RuntimeError as e:
            error_msg = str(e)
            
            # 🎯 关键：单个 story 失败不中断整体流程
            if "cancel scope" in error_msg.lower():
                self.logger.warning(
                    f"Cancel scope error for {story['id']} (non-fatal): {error_msg}"
                )
            else:
                self.logger.error(f"RuntimeError for {story['id']}: {error_msg}")
            
            results.append({'id': story['id'], 'status': 'error', 'error': error_msg})
            
            # 继续处理下一个 story
            continue
        
        except Exception as e:
            self.logger.error(f"Exception for {story['id']}: {e}")
            results.append({'id': story['id'], 'status': 'exception', 'error': str(e)})
            continue
    
    return {'stories': results, 'total': len(stories)}
```

---

### 方案 4: SDKCancellationManager 强制确认机制【已实现，需验证】

#### 验证清单

确认以下逻辑已在代码中实现：

- [ ] `wait_for_cancellation_complete()` 使用 0.5s 轮询间隔
- [ ] `confirm_safe_to_proceed()` 检查双条件：
  - call_id 不在 `active_sdk_calls` 中
  - 对应 `cancelled_calls` 记录的 `cleanup_completed=True`
- [ ] `detect_cross_task_risk()` 记录创建任务和当前任务 ID

#### 验证方法

```python
# 在 epic_driver.py 或测试中添加验证
from autoBMAD.epic_automation.monitoring import get_cancellation_manager

manager = get_cancellation_manager()
stats = manager.get_statistics()

print(f"Cross-task violations: {stats.get('cross_task_violations', 0)}")
print(f"Cancel after success: {stats.get('cancel_after_success', 0)}")
```

---

## 四、实施顺序

### Phase 1: 关键修复（立即执行）

1. ✅ **方案 2**: SM Agent 错误处理增强
   - 增加 RuntimeError 捕获
   - 增加 `_verify_stories_created()` 方法
   - 测试验证：重新运行 Epic 1，观察日志

2. ✅ **方案 3**: Epic Driver 间隔控制
   - 主循环中每次 SDK 调用后增加 `await asyncio.sleep(0.5)`
   - 测试验证：连续处理多个 story

### Phase 2: 语义优化（短期完善）

3. ✅ **方案 1**: SafeClaudeSDK 清理错误容忍
   - SDKMessageTracker 增加 `has_valid_result()` 判断
   - execute() 方法增加结果追踪逻辑
   - 测试验证：模拟清理阶段错误

### Phase 3: 验证与监控（中期保障）

4. ✅ **方案 4**: SDKCancellationManager 验证
   - 确认现有实现符合双条件验证
   - 增加统计报告输出
   - 长期监控跨任务违规数量

---

## 五、验证标准

### 5.1 功能验证

```bash
# 运行 Epic 1 完整流程
python -m autoBMAD.epic_automation.epic_driver \
    docs/epics/epic-1-core-algorithm-foundation.md \
    --source-dir src \
    --test-dir tests
```

**预期结果**:
- ✅ 4 个 story 文件成功创建
- ✅ 日志中无 "Attempted to exit cancel scope" 错误（或仅有 WARNING 级别且流程继续）
- ✅ Epic 流程正常完成

### 5.2 日志验证

**关键日志特征**:

```
# 成功路径
[SM Agent] Stories created successfully
[SDK Success] Claude SDK result: Perfect! I've successfully created...
[SDK Tracking] Completed: sdk_execute (duration=126.82s)

# 降级处理路径（可接受）
[SafeClaudeSDK] Cancel scope error in cleanup phase, but SDK already returned valid result. Treating as success.
[SM Agent] Stories verified on disk despite cleanup error. Treating as success.
```

### 5.3 统计验证

```python
# 在 epic_driver.py 末尾添加
manager = get_cancellation_manager()
report = manager.generate_report(save_to_file=True)

print("\n" + "="*70)
print("SDK Cancellation Manager Report")
print("="*70)
manager.print_summary()
```

**健康指标**:
- `cross_task_violations` = 0（理想）或保持低水平
- `cancel_after_success` > 0 可接受（说明清理阶段有噪声但功能完成）
- `success_rate` > 0.9

---

## 六、回滚方案

如果修复引入新问题：

1. **快速回滚**: 恢复以下文件到当前版本
   - `autoBMAD/epic_automation/sm_agent.py`
   - `autoBMAD/epic_automation/epic_driver.py`

2. **保留安全改动**: 以下可保留
   - `await asyncio.sleep(0.5)` 间隔（无副作用）
   - RuntimeError 日志记录（只读操作）

3. **临时降噪**: 使用自定义 asyncio exception handler
   ```python
   def exception_handler(loop, context):
       exception = context.get('exception')
       if isinstance(exception, RuntimeError):
           if 'cancel scope' in str(exception).lower():
               logger.warning(f"Suppressed cancel scope error: {exception}")
               return
       loop.default_exception_handler(context)
   
   asyncio.get_event_loop().set_exception_handler(exception_handler)
   ```

---

## 七、相关文档

- `CANCEL_SCOPE_CROSS_TASK_SOLUTION.md` - 通用解决方案
- `CANCEL_SCOPE_FIX_DETAILED_PLAN.md` - 详细修复计划
- `QUALITY_GATES_FIX_IMPLEMENTATION_REPORT.md` - 质量门控修复报告（可复用模式）
- `docs/CANCEL_SCOPE_CROSS_TASK_FIX.md` - 原理与最佳实践

---

## 八、项目记忆引用

本方案遵循以下项目约束：

1. **Cancel Scope禁止跨Task操作** (memoryId: 66bae362)
2. **避免连续异步SDK调用导致cancel scope跨任务退出** (memoryId: 2da35646)
3. **SDK取消成功的资源清理双条件验证** (memoryId: 07aa8896)
4. **RuntimeError不中断工作流** (memoryId: 2044c4ab)
5. **SDK取消管理器架构设计与强制确认机制** (memoryId: 119d6053)

---

**修复负责人**: AI Assistant  
**文档版本**: 1.0  
**最后更新**: 2026-01-10 18:35

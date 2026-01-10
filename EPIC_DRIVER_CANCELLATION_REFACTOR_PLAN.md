# Epic Driver 取消机制重构方案

## 📋 概述

本文档详细分析当前 Epic Driver 在处理 asyncio 取消信号时的问题，并提供三个分层的解决方案，旨在实现：

1. **SDK 层完全封装 cancel/cancel scope 错误**
2. **EpicDriver 仅根据业务结果和核心状态值驱动 Dev-QA 循环**
3. **asyncio 底层信号与业务逻辑完全解耦**

---

## 🎯 核心设计原则

### 1. 职责分层清晰

```
┌─────────────────────────────────────────────────────────┐
│ Epic 层（run_epic）                                      │
│ - 处理整个 epic 运行的取消（Ctrl+C / 外部停止）          │
│ - 统一捕获 asyncio.CancelledError 并优雅退出             │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ Story 层（process_story / EpicDriver）                   │
│ - 只根据核心状态值驱动 Dev-QA 循环                       │
│ - 不解释 asyncio.CancelledError                         │
│ - 不把底层信号映射为业务状态（cancelled/failed）          │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ Agent 层（DevAgent / QAAgent）                           │
│ - 返回业务结果：True/False                               │
│ - 抛出业务异常（非 asyncio 异常）                        │
│ - 更新核心状态值到 story 文档                            │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│ SDK 层（SafeClaudeSDK + SDKCancellationManager）         │
│ - 封装所有 cancel/cancel scope 错误                      │
│ - 判断有效结果，决定返回 True/False                      │
│ - 确保资源清理完成后才返回                               │
│ - 不向上抛 asyncio.CancelledError                       │
└─────────────────────────────────────────────────────────┘
```

### 2. 核心约束

- **SDK 层**：所有异步运行时错误必须在此层封装，对外只暴露业务语义（True/False）
- **EpicDriver 层**：只根据核心状态值（Draft/Ready for Review/Done）决定 Dev-QA 循环走向
- **不使用 SDK 返回值驱动循环**：Dev-QA 循环完全由核心状态值决定，SDK 返回值仅用于日志记录

---

## 📊 当前架构问题分析

### 问题 1：SDK 层未完全封装 CancelledError

**当前代码**（`sdk_wrapper.py:603-620`）：

```python
except asyncio.CancelledError:
    # 🎯 统一处理：完全委托给管理器决策
    cancel_type = manager.check_cancellation_type(call_id)

    if cancel_type == "after_success":
        # 管理器确认工作已完成，等待清理完成
        await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
        logger.info(
            "[SafeClaudeSDK] Cancellation suppressed - "
            "SDK completed successfully (confirmed by manager)"
        )
        return True

    # 真正的取消
    logger.warning("SDK execution was cancelled (confirmed by manager)")
    # 等待清理完成
    await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
    raise  # ⚠️ 问题：重新抛出 CancelledError
```

**问题**：
- ✅ "成功后的取消"已经封装（返回 True）
- ❌ "没结果的取消"仍然把 `asyncio.CancelledError` 抛给上层
- **影响**：上层（EpicDriver）需要处理这个底层信号

### 问题 2：EpicDriver 解释了 asyncio 底层信号

**当前代码**（`epic_driver.py:1267-1289`）：

```python
async def process_story(self, story: "dict[str, Any]") -> bool:
    story_path = story["path"]
    story_id = story["id"]
    logger.info(f"Processing story {story_id}: {story_path}")

    try:
        # No external timeout - rely on SDK max_turns configuration
        return await self._process_story_impl(story)
    except asyncio.CancelledError:  # ⚠️ 问题：解释底层信号
        logger.info(f"Story processing cancelled for {story_path}")
        return False  # ⚠️ 影响业务逻辑
    except RuntimeError as e:
        # ... 省略 ...
```

**问题**：
- EpicDriver 把 `asyncio.CancelledError` 解释成"story 被取消"
- 用 `return False` 影响 Dev-QA 循环走向
- 违背了"只根据业务结果和核心状态值驱动"的原则

### 问题 3：状态值映射不符合业务语义

**当前映射**（`story_parser.py:102-110`）：

```python
CORE_TO_PROCESSING_MAPPING = {
    CORE_STATUS_DRAFT: "pending",
    CORE_STATUS_READY_FOR_DEVELOPMENT: "pending",
    CORE_STATUS_IN_PROGRESS: "in_progress",
    CORE_STATUS_READY_FOR_REVIEW: "review",
    CORE_STATUS_READY_FOR_DONE: "review",
    CORE_STATUS_DONE: "completed",
    CORE_STATUS_FAILED: "failed",
}
```

**反向映射**（当前设计）：
```python
"cancelled" → "Draft"
"error"     → "Draft"
```

**问题**：
- `cancelled`/`error` 映射到 `Draft` 失去了"可继续开发"的语义
- 需要人工重新激活，不利于自动恢复

---

## 🔧 解决方案

### 方案 1：SDK 层完全封装 cancel/cancel scope 错误

#### 目标

SDK 层不再向上抛出 `asyncio.CancelledError`，所有取消/错误都转换为业务结果（True/False）。

#### 实施步骤

**步骤 1.1：修改 SafeClaudeSDK 的 CancelledError 处理**

**文件**：`autoBMAD/epic_automation/sdk_wrapper.py`

**位置**：`_execute_with_recovery()` 方法的 `except asyncio.CancelledError` 分支（约 603-620 行）

**修改内容**：

```python
except asyncio.CancelledError:
    # 🎯 统一处理：完全委托给管理器决策
    cancel_type = manager.check_cancellation_type(call_id)

    if cancel_type == "after_success":
        # 管理器确认工作已完成，等待清理完成
        await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
        logger.info(
            "[SafeClaudeSDK] Cancellation suppressed - "
            "SDK completed successfully (confirmed by manager)"
        )
        return True

    # 🎯 修改：真正的取消也不向上抛，而是返回 False
    logger.warning("SDK execution was cancelled before completion (confirmed by manager)")
    # 等待清理完成
    await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
    logger.info("[SafeClaudeSDK] Cancellation handled at SDK layer, returning False")
    return False  # ✅ 改为返回 False，不再 raise
```

**步骤 1.2：同步修改 _execute_with_isolated_scope 方法**

**文件**：`autoBMAD/epic_automation/sdk_wrapper.py`

**位置**：`_execute_with_isolated_scope()` 方法的 `except asyncio.CancelledError` 分支（约 700-710 行）

**修改内容**：

```python
except asyncio.CancelledError:
    cancel_type = manager.check_cancellation_type(call_id)

    if cancel_type == "after_success":
        await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
        logger.info("[SafeClaudeSDK] Cancellation suppressed (isolated scope)")
        return True

    # 🎯 修改：不再 raise，改为返回 False
    logger.warning("SDK execution was cancelled (isolated scope)")
    await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
    logger.info("[SafeClaudeSDK] Cancellation handled at SDK layer (isolated scope), returning False")
    return False  # ✅ 改为返回 False
```

**步骤 1.3：更新 _run_isolated_generator_with_manager 方法**

**文件**：`autoBMAD/epic_automation/sdk_wrapper.py`

**位置**：`_run_isolated_generator_with_manager()` 方法的 `except asyncio.CancelledError` 分支（约 884-893 行）

**修改内容**：

```python
except asyncio.CancelledError:
    logger.warning("Claude SDK execution was cancelled")

    try:
        await self.message_tracker.stop_periodic_display()
    except Exception as e:
        logger.debug(f"Error stopping display task: {e}")

    # 🎯 修改：不再重新抛出，而是返回 False
    logger.info("[SafeClaudeSDK] Generator cancelled, returning False")
    return False  # ✅ 改为返回 False，不再 raise
```

#### 预期效果

- ✅ SDK 层完全封装所有 cancel/cancel scope 错误
- ✅ 对外只暴露业务语义：True（成功）/ False（失败/取消）
- ✅ 上层（Agent/EpicDriver）不再收到 `asyncio.CancelledError`

---

### 方案 2：EpicDriver 移除 asyncio 信号处理

#### 目标

EpicDriver 的 `process_story` 和 `_process_story_impl` 不再捕获 `asyncio.CancelledError`，让这类信号自然传播到最外层（`run_epic` 或 `__main__`）。

#### 实施步骤

**步骤 2.1：移除 process_story 中的 CancelledError 处理**

**文件**：`autoBMAD/epic_automation/epic_driver.py`

**位置**：`process_story()` 方法（约 1267-1303 行）

**修改前**：

```python
async def process_story(self, story: "dict[str, Any]") -> bool:
    story_path = story["path"]
    story_id = story["id"]
    logger.info(f"Processing story {story_id}: {story_path}")

    try:
        return await self._process_story_impl(story)
    except asyncio.CancelledError:  # ❌ 移除
        logger.info(f"Story processing cancelled for {story_path}")
        return False
    except RuntimeError as e:
        # ... 保留 RuntimeError 处理 ...
```

**修改后**：

```python
async def process_story(self, story: "dict[str, Any]") -> bool:
    """
    Process a single story through Dev-QA cycle.

    Note: Story documents are created by SM agent during parse_epic() phase.
    This method only executes Dev-QA loop for each story.

    Args:
        story: Story dictionary with path and metadata (created by SM agent)

    Returns:
        True if story completed successfully (Done or Ready for Done), False otherwise
    
    Raises:
        asyncio.CancelledError: 当整个 epic 运行被外部取消时，向上传播
    """
    story_path = story["path"]
    story_id = story["id"]
    logger.info(f"Processing story {story_id}: {story_path}")

    try:
        return await self._process_story_impl(story)
    # ✅ 移除了 asyncio.CancelledError 的捕获，让它自然向上传播
    except RuntimeError as e:
        error_msg = str(e)

        # 🎯 关键：cancel scope 错误特殊处理
        if "cancel scope" in error_msg.lower():
            logger.warning(
                f"Cancel scope error for {story_id} (non-fatal): {error_msg}"
            )
            # 单个 story 失败不中断整体流程
            return False
        else:
            # 其他 RuntimeError
            logger.error(f"RuntimeError for {story_id}: {error_msg}")
            return False
```

**步骤 2.2：移除 _process_story_impl 中的 CancelledError 处理**

**文件**：`autoBMAD/epic_automation/epic_driver.py`

**位置**：`_process_story_impl()` 方法（约 1305-1322 行）

**修改前**：

```python
async def _process_story_impl(self, story: "dict[str, Any]") -> bool:
    story_path = story["path"]

    try:
        return await self._execute_story_processing(story)
    except asyncio.CancelledError:  # ❌ 移除
        logger.info(f"Story processing cancelled for {story_path}")
        return False
```

**修改后**：

```python
async def _process_story_impl(self, story: "dict[str, Any]") -> bool:
    """
    Internal implementation of story processing.

    Args:
        story: Story dictionary with path and metadata

    Returns:
        True if story completed successfully, False otherwise
    
    Raises:
        asyncio.CancelledError: 向上传播到 process_story
    """
    # ✅ 移除了所有 try-except，直接调用
    return await self._execute_story_processing(story)
```

**步骤 2.3：在 run_epic 顶层统一捕获 CancelledError**

**文件**：`autoBMAD/epic_automation/epic_driver.py`

**位置**：`run_epic()` 方法的外层（需要确认是否已经存在）

**确保存在以下逻辑**：

```python
async def run_epic(self) -> bool:
    """
    Run the complete epic workflow.
    
    Returns:
        True if epic completed successfully, False otherwise
    """
    try:
        # ... 现有的 epic 处理逻辑 ...
        
        # Dev-QA 循环
        for story in stories:
            try:
                # ✅ process_story 可能会传播 CancelledError
                success = await self.process_story(story)
                # ... 根据 success 和核心状态值决定下一步 ...
            except asyncio.CancelledError:
                # 🎯 在 epic 层统一处理取消
                logger.warning(
                    f"[Epic Level] Story processing interrupted by cancellation signal. "
                    f"Epic execution will terminate gracefully."
                )
                # 不改变 story 的业务状态，只记录 epic 被取消
                raise  # 继续向上传播，让最外层（__main__）处理
                
    except asyncio.CancelledError:
        # 🎯 Epic 层面的取消：整个运行被外部中止
        logger.info(
            "[Epic Cancelled] Epic execution cancelled by external signal (Ctrl+C / task.cancel())"
        )
        # 可以在这里做必要的清理工作
        # 不返回 False，而是重新抛出，让调用者知道这是取消而非失败
        raise
```

**步骤 2.4：移除 _handle_graceful_cancellation 的调用**

由于不再在 story 层捕获 `CancelledError`，相关的 `_handle_graceful_cancellation()` 调用也需要移除或调整为只在真正需要的地方（比如显式 API 取消）才调用。

#### 预期效果

- ✅ EpicDriver 不再把 `asyncio.CancelledError` 解释为业务失败
- ✅ story 层不再因为底层取消信号被标记为 `cancelled` 或 `failed`
- ✅ `CancelledError` 只在最外层（Epic 或 __main__）被捕获，表示"整个运行被中止"

---

### 方案 3：Dev-QA 循环完全基于核心状态值驱动

#### 目标

Dev-QA 循环的决策逻辑**只依赖核心状态值**（Draft/Ready for Review/Done 等），不使用 SDK 返回值或任何 asyncio 信号。

#### 核心逻辑设计

```python
# Dev-QA 循环的决策树（伪代码）
while iteration <= max_cycles:
    # 1. 读取当前核心状态
    current_status = await parse_story_status(story_path)
    
    # 2. 根据状态决定下一步
    if current_status == "Done":
        logger.info("Story completed (status: Done)")
        return True  # 结束循环
    
    elif current_status == "Ready for Done":
        logger.info("Story ready for done (status: Ready for Done)")
        return True  # 结束循环
    
    elif current_status in ["Draft", "Ready for Development"]:
        # 需要开发
        logger.info(f"Starting Dev phase (current status: {current_status})")
        await execute_dev_phase(story_path, iteration)
        # ⚠️ 不使用返回值，继续循环
        
    elif current_status == "In Progress":
        # 继续开发
        logger.info(f"Continuing Dev phase (current status: {current_status})")
        await execute_dev_phase(story_path, iteration)
        
    elif current_status == "Ready for Review":
        # 需要 QA
        logger.info(f"Starting QA phase (current status: {current_status})")
        await execute_qa_phase(story_path)
        # ⚠️ 不使用返回值，继续循环
        
    elif current_status == "Failed":
        # 失败状态，可以选择重试或退出
        logger.warning(f"Story in failed state (status: {current_status})")
        # 选项 1：重试开发
        await execute_dev_phase(story_path, iteration)
        # 选项 2：退出循环
        # return False
    
    else:
        logger.warning(f"Unknown status: {current_status}, attempting development")
        await execute_dev_phase(story_path, iteration)
    
    # 3. 增加迭代计数
    iteration += 1
    
    # 4. 短暂延迟，等待状态更新
    await asyncio.sleep(1.0)

# 超过最大循环次数
logger.warning(f"Max cycles reached ({max_cycles})")
return False
```

#### 实施步骤

**步骤 3.1：重构 _execute_story_processing 方法**

**文件**：`autoBMAD/epic_automation/epic_driver.py`

**位置**：`_execute_story_processing()` 方法（约 1324-1407 行）

**核心修改**：

1. 移除对 `dev_success` 和 `qa_passed` 布尔值的依赖
2. 每次循环开始时读取核心状态值
3. 根据核心状态值决定执行 Dev 还是 QA
4. 只在状态为 `Done` 或 `Ready for Done` 时返回 True

**修改后的核心逻辑**：

```python
async def _execute_story_processing(self, story: "dict[str, Any]") -> bool:
    """
    Core story processing logic - driven purely by core status values.
    
    Dev-QA 循环完全由核心状态值驱动，不依赖 SDK 返回值。
    """
    story_path = story["path"]
    story_id = story["id"]

    try:
        # 检查是否已完成
        existing_status: dict[str, Any] = await self.state_manager.get_story_status(
            story_path
        )
        if existing_status and existing_status.get("status") in ["completed", "qa_waived"]:
            logger.info(f"Story already processed: {story_path} (status: {existing_status.get('status')})")
            return True

        # 🎯 核心改动：循环由核心状态值驱动
        iteration = 1
        max_dev_qa_cycles = 10
        
        while iteration <= max_dev_qa_cycles:
            logger.info(
                f"[Epic Driver] Dev-QA cycle #{iteration} for {story_path}"
            )

            # 1️⃣ 读取当前核心状态值
            current_status = await self._parse_story_status(story_path)
            logger.info(f"[Cycle {iteration}] Current status: {current_status}")

            # 2️⃣ 根据核心状态值决定下一步
            if current_status in ["Done", "Ready for Done"]:
                # ✅ 终态：故事完成
                logger.info(f"Story {story_id} completed (Status: {current_status})")
                return True
            
            elif current_status in ["Draft", "Ready for Development"]:
                # 需要开发
                logger.info(f"[Cycle {iteration}] Executing Dev phase (status: {current_status})")
                await self.execute_dev_phase(story_path, iteration)
                # ⚠️ 不检查返回值，继续循环
                
            elif current_status == "In Progress":
                # 继续开发
                logger.info(f"[Cycle {iteration}] Continuing Dev phase (status: {current_status})")
                await self.execute_dev_phase(story_path, iteration)
                
            elif current_status == "Ready for Review":
                # 需要 QA
                logger.info(f"[Cycle {iteration}] Executing QA phase (status: {current_status})")
                await self.execute_qa_phase(story_path)
                # ⚠️ 不检查返回值，继续循环
                
            elif current_status == "Failed":
                # 失败状态，尝试重新开发
                logger.warning(f"[Cycle {iteration}] Story in failed state, retrying Dev phase")
                await self.execute_dev_phase(story_path, iteration)
            
            else:
                # 未知状态，尝试开发
                logger.warning(f"[Cycle {iteration}] Unknown status '{current_status}', attempting Dev phase")
                await self.execute_dev_phase(story_path, iteration)

            # 3️⃣ 等待 SDK 清理 + 状态更新
            await asyncio.sleep(1.0)

            # 4️⃣ 增加迭代计数
            iteration += 1

        # 超过最大循环次数
        logger.warning(
            f"Reached maximum Dev-QA cycles ({max_dev_qa_cycles}) for {story_path}"
        )
        return False

    except Exception as e:
        logger.error(f"Failed to process story {story_path}: {e}")
        await self.state_manager.update_story_status(
            story_path=story_path, status="error", error=str(e)
        )
        return False
```

**步骤 3.2：调整 execute_dev_phase 和 execute_qa_phase**

这两个方法的返回值不再被使用，但仍然保留返回值以便日志记录和监控。

**重要**：确保这两个方法内部：
- 不因为 SDK 返回 False 就中断流程
- 只负责调用 Agent，让 Agent 更新核心状态值
- 所有决策逻辑都由上层的 `_execute_story_processing` 根据状态值来做

**步骤 3.3：更新状态值映射（可选）**

如果需要让 `cancelled`/`error` 状态更容易恢复，可以调整映射：

**文件**：`autoBMAD/epic_automation/story_parser.py`

**位置**：反向映射逻辑（约 110-120 行，具体视实现而定）

**建议映射**：

```python
# 处理状态值 → 核心状态值（用于 Markdown 显示）
PROCESSING_TO_CORE_MAPPING = {
    "pending": "Draft",
    "in_progress": "In Progress",
    "review": "Ready for Review",
    "completed": "Done",
    "failed": "Failed",
    "cancelled": "Ready for Development",  # ✅ 改为可继续开发
    "error": "Ready for Development",      # ✅ 改为可继续开发
}
```

**说明**：
- 这样当 story 被标记为 `cancelled` 或 `error` 时
- 在下一次循环中会被识别为 `Ready for Development`
- 自动进入 Dev 阶段，无需人工干预

#### 预期效果

- ✅ Dev-QA 循环完全由核心状态值驱动
- ✅ SDK 返回值只用于日志记录，不影响循环决策
- ✅ 状态值语义清晰：`Ready for Development` = 可以自动进入开发
- ✅ 循环逻辑简单明确，易于理解和维护

---

## 📝 实施优先级和顺序

### 阶段 1：SDK 层封装（方案 1）

**优先级**：🔴 高

**原因**：这是基础，必须先确保 SDK 层不再向上抛 CancelledError

**验证方法**：
1. 运行现有测试，确认 SDK 调用不再抛出 `asyncio.CancelledError`
2. 检查日志，确认所有取消都被转换为 False 返回值
3. 确认 `SDKCancellationManager` 的双条件验证正常工作

### 阶段 2：EpicDriver 清理（方案 2）

**优先级**：🔴 高

**原因**：在 SDK 层封装完成后，可以安全移除 EpicDriver 的 asyncio 处理

**验证方法**：
1. 确认 `process_story` 不再捕获 `CancelledError`
2. 确认 Ctrl+C 时能在 Epic 层统一处理
3. 确认 story 状态不会因为取消信号被错误标记

### 阶段 3：状态驱动重构（方案 3）

**优先级**：🟡 中

**原因**：这是逻辑优化，可以在前两个阶段稳定后再进行

**验证方法**：
1. 跑一个完整的 epic，确认循环只根据状态值决策
2. 手动修改 story 状态，验证循环能正确响应
3. 检查日志，确认没有"SDK 返回 False 导致循环终止"的情况

---

## 🧪 测试验证清单

### 单元测试

- [ ] SDK 层封装测试
  - [ ] 有结果 + cancel scope 错误 → 返回 True
  - [ ] 无结果 + CancelledError → 返回 False（不抛异常）
  - [ ] 资源清理验证（active_sdk_calls + cleanup_completed）

- [ ] EpicDriver 测试
  - [ ] process_story 不捕获 CancelledError
  - [ ] run_epic 在顶层统一处理取消
  - [ ] story 状态不受取消信号影响

- [ ] 状态驱动逻辑测试
  - [ ] 循环根据状态值正确决策
  - [ ] Done/Ready for Done → 结束循环
  - [ ] Draft/Ready for Development → 执行 Dev
  - [ ] Ready for Review → 执行 QA

### 集成测试

- [ ] 完整 epic 运行测试
  - [ ] 多个 story 顺序处理
  - [ ] 状态转换正确
  - [ ] 日志清晰易读

- [ ] 取消场景测试
  - [ ] Ctrl+C 能优雅退出
  - [ ] 取消不影响已完成的 story 状态
  - [ ] SDK 资源正确清理

- [ ] 错误恢复测试
  - [ ] cancelled 状态的 story 能自动重试
  - [ ] error 状态的 story 能继续开发
  - [ ] 循环不会因为单次失败而终止

---

## 📊 预期收益

### 架构收益

1. **职责分层清晰**
   - SDK 层：封装所有异步运行时细节
   - EpicDriver 层：纯业务逻辑编排
   - 无耦合，易维护

2. **错误处理统一**
   - asyncio 信号只在最外层处理
   - 业务错误通过返回值/异常传递
   - 不会混淆"技术取消"和"业务失败"

3. **状态驱动简单**
   - 循环逻辑一目了然
   - 状态值语义明确
   - 易于调试和追踪

### 稳定性收益

1. **减少错误传播**
   - SDK 层的问题不会冒泡到业务层
   - 单个 story 的问题不会影响整个 epic

2. **容错能力增强**
   - cancelled/error 状态可自动恢复
   - 循环不依赖脆弱的布尔返回值

3. **可测试性提高**
   - 每层职责单一，易于单独测试
   - Mock 和 stub 更简单

### 可维护性收益

1. **代码可读性**
   - 去掉了嵌套的 try-except
   - 状态驱动逻辑清晰
   - 日志层次分明

2. **扩展性**
   - 新增状态值只需要扩展状态机
   - 新增 Agent 不影响 EpicDriver
   - SDK 层的改动不影响上层

---

## 🚨 风险和注意事项

### 风险 1：现有测试可能失败

**原因**：修改了异常处理逻辑

**缓解措施**：
1. 先在开发分支实施
2. 逐个修复失败的测试
3. 确保覆盖率不下降

### 风险 2：状态值映射改动影响已有数据

**原因**：`cancelled`/`error` 的映射改变

**缓解措施**：
1. 数据库迁移脚本
2. 兼容性处理（同时支持旧映射）
3. 逐步切换

### 风险 3：性能影响

**原因**：每次循环都要读取状态文件

**缓解措施**：
1. 状态值缓存
2. 只在必要时刷新
3. 监控 I/O 开销

---

## 📚 参考文档

- `autoBMAD/epic_automation/sdk_wrapper.py` - SDK 封装实现
- `autoBMAD/epic_automation/epic_driver.py` - EpicDriver 实现
- `autoBMAD/epic_automation/monitoring/sdk_cancellation_manager.py` - 取消管理器
- `状态值分析报告.md` - 状态值体系说明
- `状态系统架构分析报告.md` - 状态系统架构

---

## ✅ 总结

本方案通过三层改动，实现了：

1. **SDK 层完全封装异步运行时细节**
   - 不再向上抛 `asyncio.CancelledError`
   - 对外只暴露业务结果（True/False）

2. **EpicDriver 只关注业务逻辑**
   - 移除所有 asyncio 信号处理
   - 只根据核心状态值驱动 Dev-QA 循环

3. **状态驱动的清晰流程**
   - 循环逻辑简单明确
   - 状态语义清晰
   - 易于维护和扩展

**核心原则**：分层职责清晰，技术细节封装在底层，业务逻辑只关注业务语义。

---

**文档版本**：1.0  
**创建日期**：2026-01-10  
**最后更新**：2026-01-10

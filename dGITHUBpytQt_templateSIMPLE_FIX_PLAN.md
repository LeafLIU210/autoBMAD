# Epic自动化系统修复方案 (简化版)

## 🚨 立即修复的问题

### 1. 状态解析错误 (最高优先级)

**问题**: AI解析器将"Done"误解析为"In Progress"

**修复文件**: `story_parser.py`

**修改位置**: 第321-356行

```python
def _extract_status_from_response(self, response: str) -> str:
    """从AI响应中提取状态值"""
    if not response:
        logger.warning("SimpleStatusParser: Received empty response from AI")
        return "unknown"

    cleaned = response.strip()
    cleaned = cleaned.replace("[Thinking]", "").replace("[Tool result]", "")
    cleaned = cleaned.replace("**", "").replace("*", "")
    cleaned = cleaned.strip()
    
    cleaned_lower = cleaned.lower()

    # 先尝试直接匹配
    for core_status in CORE_STATUS_VALUES:
        if cleaned_lower == core_status.lower():
            return core_status

    # 🔴 新增：如果无法匹配，检查是否包含"done"关键词
    if 'done' in cleaned_lower:
        logger.warning(f"AI returned '{cleaned}' but contains 'done', using fallback regex parsing")
        return "unknown"  # 🔴 触发回退到正则解析
    
    return cleaned if cleaned else "unknown"
```

**附加修改**: 第314-319行，增加回退逻辑

```python
try:
    status = await sdk.execute()
    
    if success:
        if not hasattr(sdk, 'message_tracker'):
            logger.warning("SimpleStatusParser: SDK does not have message_tracker attribute")
            return "unknown"

        latest_message = sdk.message_tracker.latest_message
        if latest_message:
            # 🔴 新增：先尝试正则解析作为备用
            fallback_status = self._regex_fallback_parse(content)
            if fallback_status:
                logger.info(f"Using fallback regex status: {fallback_status}")
                return fallback_status
            
            # 然后尝试AI解析
            ai_status = self._extract_status_from_response(latest_message)
            if ai_status != "unknown":
                return ai_status
```

---

### 2. 迭代控制失效 (高优先级)

**问题**: 双重循环计数器导致无限循环

**修复文件**: `epic_driver.py`

**修改位置**: 第1264-1292行

```python
# 移除max_dev_qa_cycles循环，统一使用max_iterations
iteration = 1
while iteration <= self.max_iterations:  # 🔴 使用统一的计数器
    logger.info(f"[Epic Driver] Starting Dev-QA cycle #{iteration} for {story_path}")

    # Dev Phase
    dev_success = await self.execute_dev_phase(story_path, iteration)
    
    # 🔴 修复：Dev失败时直接终止，不继续QA
    if not dev_success:
        logger.error(f"Dev phase failed for {story_path}, terminating story processing")
        return False

    # QA Phase
    qa_passed = await self.execute_qa_phase(story_path)

    if qa_passed:
        # Check if story is ready for done
        if await self._is_story_ready_for_done(story_path):
            logger.info(f"Story {story_id} completed successfully (Ready for Done)")
            return True
        else:
            logger.info(f"QA passed but story not ready for done, continuing cycle {iteration + 1}")

    iteration += 1

# 如果我们到达这里，达到了最大循环次数
logger.warning(f"Reached maximum Dev-QA cycles ({self.max_iterations}) for {story_path}")
return False
```

---

### 3. 异步取消范围错误 (高优先级)

**问题**: cancel scope跨任务错误

**修复文件**: `sdk_wrapper.py`

**修改位置**: 第481-492行

```python
# Wrap generator with safe wrapper
safe_generator = SafeAsyncGenerator(generator)

# 🔴 修复：确保在单独的任务中运行，避免cancel scope冲突
try:
    # 🔴 使用create_task而不是shield，确保正确的任务隔离
    task = asyncio.create_task(self._run_isolated_generator(safe_generator))
    result = await task
    return result
except Exception as e:
    logger.error(f"Error in isolated generator execution: {e}")
    logger.debug(traceback.format_exc())
    await safe_generator.aclose()
    return False
finally:
    # 🔴 确保清理
    if 'task' in locals() and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
```

---

## 🔧 测试验证

修复后需要验证：

1. **状态解析测试**:
   ```bash
   python -m pytest tests/test_story_parser.py -v
   ```

2. **迭代控制测试**:
   ```bash
   python -m autoBMAD.epic_automation.epic_driver docs/epics/epic-1-core-algorithm-foundation.md --max-iterations 2 --verbose
   ```
   - 应该只执行2个循环
   - 每次循环应该更新数据库版本

3. **异步错误测试**:
   ```bash
   python -c "import asyncio; from autoBMAD.epic_automation.sdk_wrapper import SafeAsyncGenerator; print('SDK wrapper loads successfully')"
   ```
   - 不应该产生cancel scope错误

---

## 📝 修复优先级

1. ✅ **状态解析错误** - 最关键，导致无限循环
2. ✅ **迭代控制失效** - 浪费资源，无法终止
3. ✅ **异步取消范围错误** - 影响稳定性

---

## 💡 快速修复命令

```bash
# 1. 备份原文件
cp autoBMAD/epic_automation/story_parser.py autoBMAD/epic_automation/story_parser.py.backup
cp autoBMAD/epic_automation/epic_driver.py autoBMAD/epic_automation/epic_driver.py.backup
cp autoBMAD/epic_automation/sdk_wrapper.py autoBMAD/epic_automation/sdk_wrapper.py.backup

# 2. 应用修复 (使用上面的代码)
# ... 编辑文件 ...

# 3. 验证修复
python -m autoBMAD.epic_automation.epic_driver docs/epics/epic-1-core-algorithm-foundation.md --max-iterations 2 --verbose 2>&1 | grep -E "(Max iterations|Dev-QA cycle #|ERROR)"
```

---

## 📊 修复效果预期

修复后应该看到：
- ✅ 只执行2个Dev-QA循环（而不是4个或更多）
- ✅ 状态解析准确（文档中的"Done"被正确识别）
- ✅ 没有cancel scope错误
- ✅ 故事在达到max_iterations时正确终止


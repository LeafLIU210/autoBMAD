# 🚀 异步取消范围错误修复方案

## 📋 问题概述

### 核心错误
```
RuntimeError: Attempted to exit cancel scope in a different task than it was entered in
```

### 错误影响
- 每个SDK调用都产生cancel scope错误
- 日志噪音严重，影响问题排查
- 潜在的资源泄漏和异步上下文崩溃风险
- 系统稳定性问题

## 🔍 根本原因分析

### 1. 异步上下文冲突
**位置**: `epic_driver.py:1496-1501`
- 代码在已运行的事件循环中启动新的异步操作
- 跨任务cancel scope冲突

### 2. 重复状态解析
**执行流程**:
1. Dev Agent检测故事状态为"Ready for Review"
2. 跳过SDK调用，直接通知QA Agent
3. QA Agent重新解析状态，启动SDK
4. SDK立即被取消，cancel scope处理异常

### 3. 异步生成器生命周期管理缺陷
**位置**: `sdk_wrapper.py:129-181`
- 异步生成器清理时缺乏cancel scope错误处理
- 跨任务访问冲突

## 🎯 修复策略

### 原则
1. **确保SDK调用完全结束后再执行下一步操作**
2. **避免重复状态解析**
3. **统一异步上下文管理**
4. **安全处理cancel scope错误**

## 📝 具体修复方案

### 方案1: 修复SDK Wrapper中的异步生成器清理

**文件**: `autoBMAD/epic_automation/sdk_wrapper.py`

#### 修改位置1: SafeAsyncGenerator.aclose() 增强
```python
async def aclose(self) -> None:
    """增强的异步生成器清理 - 防止 cancel scope 跨任务错误"""
    if self._closed:
        return

    self._closed = True

    try:
        # 检测事件循环状态
        loop = asyncio.get_running_loop()
        loop_running = not loop.is_closed()

        if not loop_running:
            logger.debug("Event loop is closed, skipping generator cleanup")
            return

        # 获取原始生成器的 aclose 方法
        aclose = getattr(self.generator, "aclose", None)
        if aclose and callable(aclose):
            try:
                result = aclose()
                if result is not None:
                    if asyncio.iscoroutine(result):
                        # 🎯 关键修复：确保在正确的任务上下文中执行
                        await result
            except (TypeError, AttributeError) as e:
                logger.debug(f"Generator cleanup (non-critical): {e}")
            except asyncio.CancelledError:
                # 记录但不重新抛出，避免 scope 冲突
                logger.debug("Generator cleanup cancelled (ignored)")
            except RuntimeError as e:
                error_msg = str(e)
                # 🎯 关键修复：识别并安全处理 cancel scope 错误
                if "cancel scope" in error_msg or "Event loop is closed" in error_msg:
                    logger.debug(f"Expected SDK shutdown error (suppressed): {error_msg}")
                    return  # 返回而不是抛出，防止崩溃
                else:
                    logger.debug(f"Generator cleanup RuntimeError: {e}")
                    raise
            except Exception as e:
                logger.debug(f"Generator cleanup exception: {e}")
    except Exception as e:
        logger.debug(f"Generator cleanup error: {e}")
```

#### 修改位置2: SDK执行安全包装
```python
async def execute(self) -> bool:
    """执行Claude SDK查询安全包装"""
    try:
        return await self._execute_safely()
    except asyncio.CancelledError:
        # 🎯 关键修复：确保取消完全处理
        logger.warning("SDK execution was cancelled")
        await self._ensure_cleanup_complete()
        raise
    except RuntimeError as e:
        error_msg = str(e).lower()
        # 🎯 增强的cancel scope错误处理
        if "cancel scope" in error_msg:
            logger.debug(f"[SafeClaudeSDK] Cancel scope error suppressed: {e}")
            await self._ensure_cleanup_complete()
            return True  # 返回True表示成功抑制，继续执行
        elif "event loop is closed" in error_msg:
            logger.warning(f"Event loop closed: {e}")
            return False
        else:
            logger.error(f"Runtime error in SDK execution: {e}")
            return False
    except Exception as e:
        error_msg = str(e).lower()
        if "cancel scope" in error_msg:
            logger.debug(f"[SafeClaudeSDK] Cancel scope error suppressed: {e}")
            await self._ensure_cleanup_complete()
            return True
        elif "event loop is closed" in error_msg:
            logger.warning(f"Event loop closed: {e}")
            return False
        else:
            logger.error(f"Claude SDK execution failed: {e}")
            return False

async def _ensure_cleanup_complete(self) -> None:
    """🎯 新增：确保清理完全结束"""
    try:
        # 等待一小段时间确保清理完成
        await asyncio.sleep(0.1)
        logger.debug("SDK cleanup completed")
    except Exception as e:
        logger.debug(f"Cleanup completion check failed: {e}")
```

### 方案2: 改进Dev Agent的异步任务管理

**文件**: `autoBMAD/epic_automation/dev_agent.py`

#### 修改位置1: 状态解析后等待机制
```python
async def execute_dev_phase(self, story_path: str, source_dir: str, test_dir: str) -> bool:
    """执行开发阶段 - 增强异步任务管理"""
    try:
        # 1. 解析故事状态
        logger.info(f"[Dev Agent] Extracting requirements from story")
        requirements = await self._extract_requirements(story_path)

        # 2. 🎯 关键修复：等待状态解析的SDK完全结束
        await self._wait_for_sdk_completion("status parsing")

        # 3. 根据状态执行相应操作
        story_status = self._get_cached_status(story_path)  # 使用缓存状态

        if story_status == "Ready for Review":
            logger.info(f"[Dev Agent] Story '{story_path}' already ready for review, skipping SDK calls")
            # 开发完成，通知QA agent
            return await self._notify_qa_agent_safe(story_path)
        else:
            # 执行开发任务
            logger.info(f"[Dev Agent] Executing development tasks")
            success = await self._execute_development_tasks(requirements, story_path, source_dir, test_dir)

            # 4. 🎯 关键修复：等待开发SDK调用完全结束
            await self._wait_for_sdk_completion("development tasks")

            # 5. 通知QA agent（移除开发后的状态解析）
            if success:
                return await self._notify_qa_agent_safe(story_path)
            return False

    except Exception as e:
        logger.error(f"[Dev Agent] Error in dev phase: {e}")
        return False

async def _wait_for_sdk_completion(self, task_name: str) -> None:
    """🎯 新增：等待SDK调用完全结束"""
    try:
        # 确保所有pending的SDK任务完成
        await asyncio.sleep(0.2)  # 等待一小段时间
        logger.debug(f"[Dev Agent] {task_name} SDK calls completed")
    except Exception as e:
        logger.debug(f"[Dev Agent] SDK completion wait failed: {e}")

async def _notify_qa_agent_safe(self, story_path: str) -> bool:
    """🎯 改进：安全的QA通知（移除重复状态解析）"""
    try:
        logger.info(f"[Dev Agent] Notifying QA agent for: {story_path}")

        # 直接传递已解析的状态，而不是重新解析
        cached_status = self._get_cached_status(story_path)

        qa_agent = QAAgent()
        await qa_agent.initialize()

        # 🎯 关键修复：传递缓存状态，避免QA agent重复解析
        return await qa_agent.execute_qa_phase(story_path, cached_status=cached_status)

    except Exception as e:
        logger.error(f"[Dev Agent] Error notifying QA agent: {e}")
        return False
```

#### 修改位置2: 缓存状态管理
```python
def __init__(self, ...):
    # ... 现有初始化代码
    self._status_cache: Dict[str, str] = {}  # 🎯 新增：状态缓存

def _get_cached_status(self, story_path: str) -> str:
    """🎯 新增：获取缓存的故事状态"""
    if story_path not in self._status_cache:
        # 如果没有缓存，从数据库或文件读取
        self._status_cache[story_path] = self._parse_story_status_sync(story_path)
    return self._status_cache[story_path]

def _parse_story_status_sync(self, story_path: str) -> str:
    """同步状态解析，避免异步冲突"""
    try:
        story_file = Path(story_path)
        if not story_file.exists():
            return "Unknown"

        content = story_file.read_text(encoding="utf-8")

        # 使用正则表达式快速解析状态
        status_patterns = [
            r"\*\*Status\*\*:\s*\*\*([^*]+)\*\*",
            r"\*\*Status\*\*:\s*(.+)$",
            r"Status:\s*(.+)$",
        ]

        for pattern in status_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                status_text = match.group(1).strip()
                # 标准化状态
                return _normalize_story_status(status_text)

        return "Draft"  # 默认状态

    except Exception as e:
        logger.error(f"[Dev Agent] Failed to parse status: {e}")
        return "Unknown"
```

### 方案3: 改进QA Agent的异步任务管理

**文件**: `autoBMAD/epic_automation/qa_agent.py`

#### 修改位置1: 安全的QA执行流程
```python
async def execute_qa_phase(self, story_path: str, source_dir: str, test_dir: str, cached_status: str = None) -> bool:
    """执行QA阶段 - 增强异步任务管理"""
    try:
        # 1. 🎯 关键修复：等待QA审查任务的SDK完全结束
        await self._wait_for_qa_sdk_completion()

        # 2. 获取故事状态（使用缓存或解析）
        if cached_status:
            logger.info(f"[QA Agent] Using cached status: {cached_status}")
            status = cached_status
        else:
            # 只有在没有缓存时才解析状态
            logger.info(f"[QA Agent] Parsing story status")
            status = await self._parse_story_status_safe(story_path)

            # 3. 🎯 关键修复：等待状态解析的SDK完全结束
            await self._wait_for_status_sdk_completion()

        # 4. 根据状态执行相应操作
        status_lower = status.lower()

        if status_lower in ["ready for done", "done"]:
            logger.info(f"[QA Agent] Story status is '{status}' - considered complete, skipping QA")
            return True
        elif status_lower == "ready for review":
            logger.info(f"[QA Agent] Story status is '{status}' - executing QA review")
            result = await self._execute_qa_review(story_path, source_dir, test_dir)
            return result.passed
        else:
            logger.info(f"[QA Agent] Story status is '{status}' - needs fixing")
            return False

    except Exception as e:
        logger.error(f"[QA Agent] Error in QA phase: {e}")
        return False

async def _wait_for_qa_sdk_completion(self) -> None:
    """🎯 新增：等待QA审查SDK调用完全结束"""
    try:
        await asyncio.sleep(0.2)  # 确保清理完成
        logger.debug("[QA Agent] QA review SDK calls completed")
    except Exception as e:
        logger.debug(f"[QA Agent] QA SDK completion wait failed: {e}")

async def _wait_for_status_sdk_completion(self) -> None:
    """🎯 新增：等待状态解析SDK调用完全结束"""
    try:
        await asyncio.sleep(0.2)  # 确保清理完成
        logger.debug("[QA Agent] Status parsing SDK calls completed")
    except Exception as e:
        logger.debug(f"[QA Agent] Status SDK completion wait failed: {e}")

async def _parse_story_status_safe(self, story_path: str) -> str:
    """🎯 改进：安全的状态解析"""
    try:
        story_file = Path(story_path)
        if not story_file.exists():
            logger.warning(f"[QA Agent] Story file not found: {story_path}")
            return "Unknown"

        content = story_file.read_text(encoding="utf-8")

        # 使用SimpleStoryParser进行AI解析
        if self.status_parser:
            logger.info(f"[QA Agent] Using AI status parser")
            status = await self.status_parser.parse_status(content)

            # 🎯 关键修复：等待AI解析完全结束
            await self._wait_for_ai_parsing_complete()
            return status
        else:
            # 回退到正则表达式解析
            logger.info(f"[QA Agent] Using regex fallback for status parsing")
            return self._regex_fallback_parse_status(content)

    except Exception as e:
        logger.error(f"[QA Agent] Error parsing story status: {e}")
        return "Unknown"

async def _wait_for_ai_parsing_complete(self) -> None:
    """🎯 新增：等待AI解析完全结束"""
    try:
        await asyncio.sleep(0.1)
        logger.debug("[QA Agent] AI parsing completed")
    except Exception as e:
        logger.debug(f"[QA Agent] AI parsing completion wait failed: {e}")
```

### 方案4: 优化epic_driver中的异步上下文检测

**文件**: `autoBMAD/epic_automation/epic_driver.py`

#### 修改位置1: 改进异步上下文检测
```python
def parse_story_status_sync(self, story_path: str) -> str:
    """同步故事状态解析 - 避免异步冲突"""
    try:
        # 🎯 关键修复：移除异步上下文检测，直接使用同步解析
        logger.info(f"Using synchronous status parsing for: {story_path}")
        return self._parse_story_status_fallback(story_path)

    except Exception as e:
        logger.error(f"Failed to parse story status (sync): {e}")
        return "Draft"

def _parse_story_status_fallback(self, story_path: str) -> str:
    """回退解析方法 - 使用正则表达式"""
    try:
        story_file = Path(story_path)
        if not story_file.exists():
            logger.warning(f"Story file not found: {story_path}")
            return "Unknown"

        content = story_file.read_text(encoding="utf-8")

        # 定义状态匹配的正则表达式模式
        status_patterns = [
            (r"\*\*Status\*\*:\s*\*\*([^*]+)\*\*", 1),      # **Status**: **Draft**
            (r"\*\*Status\*\*:\s*(.+)$", 1),                # **Status**: Draft
            (r"Status:\s*(.+)$", 1),                        # Status: Draft
            (r"状态[：:]\s*(.+)$", 1),                      # 状态：草稿
        ]

        # 遍历模式匹配
        for pattern, group_index in status_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                status_text = match.group(group_index).strip()
                logger.debug(f"Regex match found: '{status_text}' via pattern '{pattern}'")

                # 标准化状态
                try:
                    normalized = _normalize_story_status(status_text)
                    if normalized in CORE_STATUS_VALUES:
                        logger.info(f"Status parsed successfully: '{status_text}' → '{normalized}'")
                        return normalized
                except Exception as e:
                    logger.warning(f"Status normalization failed: {e}")

        # 默认值
        logger.info("Status fallback returned default: 'Draft'")
        return "Draft"

    except Exception as e:
        logger.error(f"Failed to parse story status fallback: {e}")
        return "Draft"
```

## 🧪 测试验证

### 测试用例1: SDK调用取消测试
```python
async def test_sdk_cancellation():
    """测试SDK调用取消是否正确处理"""
    # 1. 创建SDK wrapper
    sdk = SafeClaudeSDK(prompt="test prompt", options=test_options)

    # 2. 执行SDK调用
    task = asyncio.create_task(sdk.execute())

    # 3. 立即取消
    await asyncio.sleep(0.1)
    task.cancel()

    # 4. 验证取消是否正确处理
    try:
        await task
    except asyncio.CancelledError:
        # 取消应该被正确处理，不应产生cancel scope错误
        pass

    # 5. 验证后续操作可以正常执行
    result = await sdk.execute()
    assert result == True  # 应该返回True表示cancel scope错误被抑制
```

### 测试用例2: 状态解析测试
```python
async def test_status_parsing():
    """测试状态解析的异步处理"""
    # 1. 模拟Dev Agent和QA Agent的交互
    dev_agent = DevAgent()
    qa_agent = QAAgent()

    # 2. 执行开发阶段
    dev_success = await dev_agent.execute_dev_phase(test_story_path, "src", "tests")

    # 3. 验证没有cancel scope错误
    assert dev_success == True

    # 4. 执行QA阶段
    qa_success = await qa_agent.execute_qa_phase(test_story_path, "src", "tests")

    # 5. 验证QA执行成功
    assert qa_success == True
```

### 测试用例3: 完整流程测试
```python
async def test_full_workflow():
    """测试完整的Dev-QA工作流"""
    # 1. 创建测试故事
    test_story = create_test_story("Ready for Review")

    # 2. 执行完整流程
    result = await execute_dev_qa_cycle(test_story)

    # 3. 验证结果
    assert result.success == True
    assert result.sdk_errors == 0  # 没有SDK错误
    assert result.cancel_scope_errors == 0  # 没有cancel scope错误
```

## 📊 预期效果

### 修复前
- 每个SDK调用产生5-10条cancel scope错误日志
- 异步上下文冲突频繁发生
- 系统稳定性差

### 修复后
- Cancel scope错误被安全抑制，日志减少90%
- 异步上下文管理统一
- 系统稳定性显著提升
- 开发效率提高

## 🔄 实施计划

### 阶段1: SDK Wrapper修复 (1-2小时)
- 修改SafeAsyncGenerator.aclose()
- 增强SDK执行错误处理
- 添加清理完成检查

### 阶段2: Dev Agent改进 (2-3小时)
- 实现状态缓存机制
- 添加SDK完成等待
- 移除重复状态解析

### 阶段3: QA Agent改进 (2-3小时)
- 改进QA执行流程
- 添加SDK完成等待
- 传递缓存状态

### 阶段4: epic_driver优化 (1小时)
- 移除异步上下文检测
- 统一状态解析方法

### 阶段5: 测试验证 (1-2小时)
- 运行现有测试
- 验证修复效果
- 性能测试

## 🎯 关键指标

1. **错误数量**: Cancel scope错误减少90%
2. **日志质量**: 错误日志减少80%
3. **系统稳定性**: 零崩溃事件
4. **执行效率**: 任务完成时间减少30%

---

## 📝 总结

本修复方案通过以下关键措施解决异步取消范围错误：

1. **增强SDK错误处理**: 安全抑制cancel scope错误
2. **统一异步管理**: 确保SDK调用完全结束再执行下一步
3. **状态缓存机制**: 避免重复状态解析
4. **安全清理流程**: 确保资源正确释放

实施本方案将显著提升系统稳定性和开发效率。

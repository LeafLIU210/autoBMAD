# Epic Driver 调试日志改进建议

## 当前状态分析

### 已有的日志信息
✅ **存在的基础日志**:
- 警告: "StatusParser not available, using fallback parsing"
- 警告: "Already in async context, using fallback parsing"
- 错误: "Failed to parse story status"

❌ **缺失的关键调试信息**:
- 未记录状态解析过程
- 未记录标准化前后状态值
- 未记录实际使用的解析方法 (AI vs 回退)
- 未记录正则表达式匹配结果

---

## 建议增加的调试信息

### 1. 增强 `_parse_story_status_fallback` 函数

**位置**: `epic_driver.py` 第1360-1403行

**建议修改**:

```python
def _parse_story_status_fallback(self, story_path: str) -> str:
    """
    Fallback parsing method using original regex patterns.

    Args:
        story_path: Path to the story markdown file

    Returns:
        Status string using original parsing logic
    """
    try:
        logger.debug(f"[Status Parse] Starting fallback parsing for: {story_path}")

        with open(story_path, encoding='utf-8') as f:
            content = f.read()

        # Try multi-line format first: ## Status\n**Value**
        match = re.search(r'##\s*Status\s*\n\s*\*\*([^*]+)\*\*', content, re.IGNORECASE | re.MULTILINE)
        if match:
            raw_status = match.group(1).strip()
            status_lower = raw_status.lower()
            logger.debug(f"[Status Parse] Multi-line bold format match: '{raw_status}' -> lowercase: '{status_lower}'")
            normalized = _normalize_story_status(status_lower)
            logger.debug(f"[Status Parse] Normalized to: '{normalized}'")
            return normalized

        # Try multi-line format: ## Status\n Value
        match = re.search(r'##\s*Status\s*\n\s*([^\n#]+)', content, re.IGNORECASE | re.MULTILINE)
        if match:
            raw_status = match.group(1).strip()
            status_lower = raw_status.lower()
            logger.debug(f"[Status Parse] Multi-line format match: '{raw_status}' -> lowercase: '{status_lower}'")
            normalized = _normalize_story_status(status_lower)
            logger.debug(f"[Status Parse] Normalized to: '{normalized}'")
            return normalized

        # Look for inline format: **Status**: **Value** or Status: Value
        logger.debug("[Status Parse] Searching for inline Status: format")
        for line_num, line in enumerate(content.split('\n'), 1):
            if 'Status:' in line:
                logger.debug(f"[Status Parse] Found Status: at line {line_num}: '{line.strip()}'")

                # Try to extract status from bold format: **Status**: **Ready for Development**
                match = re.search(r'\*\*Status\*\*:\s*\*\*([^*]+)\*\*', line, re.IGNORECASE)
                if match:
                    raw_status = match.group(1).strip()
                    status_lower = raw_status.lower()
                    logger.debug(f"[Status Parse] Inline bold format match: '{raw_status}' -> lowercase: '{status_lower}'")
                    normalized = _normalize_story_status(status_lower)
                    logger.debug(f"[Status Parse] Normalized to: '{normalized}'")
                    return normalized

                # Try to extract from regular format: Status: Ready for Development
                match = re.search(r'Status:\s*(.+)', line, re.IGNORECASE)
                if match:
                    raw_status = match.group(1).strip()
                    status_lower = raw_status.lower()
                    logger.debug(f"[Status Parse] Inline format match: '{raw_status}' -> lowercase: '{status_lower}'")
                    normalized = _normalize_story_status(status_lower)
                    logger.debug(f"[Status Parse] Normalized to: '{normalized}'")
                    return normalized

        logger.debug("[Status Parse] No status found, using default: 'Ready for Development'")
        return _normalize_story_status('Ready for Development')
    except Exception as e:
        logger.error(f"Fallback parsing failed: {e}")
        return _normalize_story_status('Ready for Development')
```

### 2. 增强 `_parse_story_status` 函数

**位置**: `epic_driver.py` 第1299-1327行

**建议修改**:

```python
async def _parse_story_status(self, story_path: str) -> str:
    """
    Parse the status field from a story markdown file using AI-powered parsing strategy.

    Args:
        story_path: Path to the story markdown file

    Returns:
        Standard core status string (e.g., 'Draft', 'Ready for Development', 'In Progress', 'Ready for Review', 'Ready for Done', 'Done', 'Failed')
        Uses AI parsing with fallback to 'Draft' if all parsing fails
    """
    try:
        logger.debug(f"[Status Parse] Parsing status for: {story_path}")

        with open(story_path, encoding='utf-8') as f:
            content = f.read()

        # Use StatusParser for AI-powered parsing strategy
        if hasattr(self, 'status_parser') and self.status_parser:
            logger.debug("[Status Parse] Using AI-powered StatusParser")
            # Note: parse_status is now async in SimpleStatusParser
            status = await self.status_parser.parse_status(content)
            logger.debug(f"[Status Parse] AI parser returned: '{status}'")
            # Normalize the status to ensure consistent format
            normalized = _normalize_story_status(status)
            logger.debug(f"[Status Parse] AI result normalized to: '{normalized}'")
            return normalized
        else:
            # Fallback to original parsing if StatusParser not available
            logger.warning("StatusParser not available, using fallback parsing")
            result = self._parse_story_status_fallback(story_path)
            logger.debug(f"[Status Parse] Fallback result: '{result}'")
            return result

    except Exception as e:
        logger.error(f"Failed to parse story status: {e}")
        return _normalize_story_status('Draft')  # Default to standard status instead of legacy format
```

### 3. 增强 `_parse_story_status_sync` 函数

**位置**: `epic_driver.py` 第1329-1358行

**建议修改**:

```python
def _parse_story_status_sync(self, story_path: str) -> str:
    """
    Synchronous wrapper for _parse_story_status.

    This method is used in synchronous contexts where async/await cannot be used.
    It checks if an event loop is running and uses the appropriate method.

    Args:
        story_path: Path to the story markdown file

    Returns:
        Standard core status string (e.g., 'Draft', 'Ready for Development', 'In Progress', 'Ready for Review', 'Ready for Done', 'Done', 'Failed')
    """
    try:
        import asyncio
        logger.debug(f"[Status Parse] Synchronous parsing for: {story_path}")

        # Check if we're already in an async context
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, we can't use asyncio.run()
            # Fall back to the fallback parsing method
            logger.warning("Already in async context, using fallback parsing")
            result = self._parse_story_status_fallback(story_path)
            logger.debug(f"[Status Parse] Sync fallback result: '{result}'")
            return result
        except RuntimeError:
            # No event loop running, safe to use asyncio.run()
            logger.debug("[Status Parse] No async context, using asyncio.run()")
            status = asyncio.run(self._parse_story_status(story_path))
            # Normalize the status to ensure consistent format
            normalized = _normalize_story_status(status)
            logger.debug(f"[Status Parse] Async result normalized to: '{normalized}'")
            return normalized
    except Exception as e:
        logger.error(f"Failed to parse story status (sync): {e}")
        return _normalize_story_status('Draft')  # Return standard status instead of legacy format
```

### 4. 在故事解析中增加状态日志

**位置**: `epic_driver.py` 第730-744行

**建议修改**:

```python
if story_file:
    logger.info(f"[Match Success] {story_id} -> {story_file.name}")
    # Parse status from story file
    status = self._parse_story_status_sync(str(story_file))
    logger.info(f"[Status Parse] Story {story_id} status: '{status}'")

    story_list.append({
        'id': story_id,
        'path': self._convert_to_windows_path(str(story_file.resolve())),
        'name': story_file.name,
        'status': status
    })
    found_stories.append(story_id)
    logger.info(f"Found story: {story_id} at {story_file} (status: {status})")
```

---

## 使用调试日志

### 启用调试日志

```bash
# 方法 1: 使用 --verbose 标志
python -m autoBMAD.epic_automation --verbose

# 方法 2: 设置环境变量
export PYTHONPATH=autoBMAD
export EPIC_AUTOMATION_LOG_LEVEL=DEBUG

# 方法 3: 在代码中设置
import logging
logging.getLogger('autoBMAD.epic_automation.epic_driver').setLevel(logging.DEBUG)
```

### 查看调试输出

启用调试后，您将看到类似以下的详细输出：

```
[Status Parse] Starting fallback parsing for: docs/stories/1.1-project-setup-infrastructure.md
[Status Parse] Multi-line bold format match: 'In Progress' -> lowercase: 'in progress'
[Status Parse] Normalized to: 'In Progress'
[Status Parse] Story 1.1 status: 'In Progress'
[Match Success] 1.1: Project Setup and Infrastructure -> 1.1-project-setup-infrastructure.md
```

---

## 调试信息的好处

### 1. 问题诊断
- 快速定位状态解析失败的原因
- 追踪状态值转换过程
- 验证正则表达式匹配

### 2. 开发调试
- 确认使用了正确的解析方法 (AI vs 回退)
- 监控状态标准化过程
- 验证默认值处理

### 3. 运维监控
- 审计状态解析决策
- 追踪故事状态变化
- 监控异常情况

### 4. 质量保证
- 验证状态解析一致性
- 确认标准化函数工作正常
- 排查状态不一致问题

---

## 实施建议

### 优先级

1. **高优先级** (立即实施)
   - `_parse_story_status_fallback` 中的调试日志
   - 故事解析中的状态日志

2. **中优先级** (计划实施)
   - `_parse_story_status` 中的调试日志
   - `_parse_story_status_sync` 中的调试日志

3. **低优先级** (可选)
   - 性能计数器
   - 详细错误堆栈跟踪

### 兼容性考虑

- 所有调试日志使用 `logger.debug()` 级别
- 默认不输出，避免干扰正常操作
- 通过 `--verbose` 标志或环境变量控制

---

**建议状态**: ✅ 推荐实施
**实施难度**: 低
**预期收益**: 高 - 显著提升调试和问题诊断能力
# 标准状态值规范 - Unified Status Standard

## 概述

本文档定义了 `autoBMAD/epic_automation` 系统中所有组件必须遵循的**统一标准状态值**，确保状态在各个组件间传递时的一致性和可理解性。

## 背景

之前系统中存在**三套不同的状态值系统**，导致状态不一致和理解困难：

1. **StateManager**: `pending`, `in_progress`, `review`, `pass`, `fail`
2. **StatusParser**: `Draft`, `Ready for Development`, `In Progress`, `Ready for Review`, `Ready for Done`, `Done`, `Failed`
3. **EpicDriver**: `sm_completed`, `error`, `failed`, `dev_completed`, `qa_completed`, `completed`, `cancelled`

## 标准状态值

### 核心状态值（用于文档和人类可读）

这些状态值是**标准状态值**，用于：
- 故事文档中的 `Status` 字段
- StatusParser 的解析结果
- 人类可读的状态显示

| 状态值 | 说明 | 阶段 |
|--------|------|------|
| `Draft` | 草稿状态，尚未准备好开发 | 初始 |
| `Ready for Development` | 准备好开发 | 准备 |
| `In Progress` | 开发进行中 | 开发 |
| `Ready for Review` | 开发完成，准备审查 | 开发完成 |
| `Ready for Done` | 审查通过，准备完成 | 审查完成 |
| `Done` | 故事已完成 | 完成 |
| `Failed` | 故事失败 | 失败 |

### 处理状态值（用于数据库和内部状态跟踪）

这些状态值用于 `StateManager` 数据库存储和内部状态跟踪：

| 处理状态值 | 对应核心状态 | 说明 |
|-----------|--------------|------|
| `pending` | `Draft` | 等待处理 |
| `in_progress` | `In Progress` | 处理进行中 |
| `review` | `Ready for Review` | 审查阶段 |
| `completed` | `Done` | 已完成 |
| `failed` | `Failed` | 处理失败 |

### 特殊状态值（用于特殊情况）

| 状态值 | 说明 | 使用场景 |
|--------|------|----------|
| `cancelled` | 已取消 | 手动取消的故事 |
| `error` | 错误 | 处理过程中出错 |

## 状态流转

### 正常流程

```
Draft → Ready for Development → In Progress → Ready for Review → Ready for Done → Done
```

### 异常流程

```
[任意状态] → Failed
[任意状态] → Cancelled
```

## 组件使用规范

### 1. StatusParser（状态解析器）

- **输入**: 故事文档内容
- **输出**: **核心状态值**（Draft, Ready for Development, In Progress, Ready for Review, Ready for Done, Done, Failed）
- **位置**: `status_parser.py:22-44` 的 `PROMPT_TEMPLATE`

### 2. StateManager（状态管理器）

- **存储**: **处理状态值**（pending, in_progress, review, completed, failed）
- **接口**: `update_story_status()`, `get_story_status()`
- **位置**: `state_manager.py:30-36` 的 `StoryStatus` 枚举

### 3. EpicDriver（Epic驱动程序）

- **输入**: StatusParser 的**核心状态值**
- **转换**: 将核心状态值转换为对应的处理状态值
- **存储**: 将处理状态值存储到 StateManager
- **位置**: `epic_driver.py` 的各阶段处理方法

### 4. Dev Agent（开发代理）

- **检查**: StatusParser 解析的**核心状态值**
- **逻辑**: 基于核心状态值决定是否跳过开发
- **输出**: 开发完成后设置状态为 `Ready for Review`

### 5. QA Agent（QA代理）

- **检查**: StatusParser 解析的**核心状态值**
- **逻辑**: 基于核心状态值决定是否跳过 QA
- **输出**: QA 完成后设置状态为 `Ready for Done` 或 `Done`

## 状态值转换映射

### 核心状态值 → 处理状态值

| 核心状态值 | → | 处理状态值 |
|-----------|---|-----------|
| `Draft` | → | `pending` |
| `Ready for Development` | → | `pending` |
| `In Progress` | → | `in_progress` |
| `Ready for Review` | → | `review` |
| `Ready for Done` | → | `review` |
| `Done` | → | `completed` |
| `Failed` | → | `failed` |

### 特殊状态值

| 特殊状态值 | 说明 |
|-----------|------|
| `cancelled` | 直接使用，不转换 |
| `error` | 直接使用，不转换 |

## 实现指南

### 1. 读取状态（从文档）

```python
# 使用 StatusParser 解析文档中的状态
parser = SimpleStatusParser(sdk_wrapper=SafeClaudeSDK)
core_status = await parser.parse_status(content)
# core_status 是核心状态值，如 "Ready for Review"
```

### 2. 转换状态（核心 → 处理）

```python
def core_to_processing_status(core_status: str) -> str:
    """将核心状态值转换为处理状态值"""
    mapping = {
        "Draft": "pending",
        "Ready for Development": "pending",
        "In Progress": "in_progress",
        "Ready for Review": "review",
        "Ready for Done": "review",
        "Done": "completed",
        "Failed": "failed",
    }
    return mapping.get(core_status, "pending")
```

### 3. 存储状态（到数据库）

```python
# 将核心状态转换为处理状态，然后存储到 StateManager
processing_status = core_to_processing_status(core_status)
await state_manager.update_story_status(
    story_path=story_path,
    status=processing_status,
    phase="dev"
)
```

### 4. 读取状态（从数据库）

```python
# 从 StateManager 读取处理状态
db_result = await state_manager.get_story_status(story_path)
processing_status = db_result['status']

# 如果需要，可以转换为核心状态（用于显示）
processing_to_core_status = {
    "pending": "Draft",
    "in_progress": "In Progress",
    "review": "Ready for Review",
    "completed": "Done",
    "failed": "Failed",
    "cancelled": "Cancelled",
    "error": "Error",
}
core_status = processing_to_core_status.get(processing_status, "Draft")
```

## 迁移计划

### 阶段 1: 更新 StateManager
- 保持现有的 `StoryStatus` 枚举不变
- 添加核心状态值与处理状态值的映射函数

### 阶段 2: 更新 StatusParser
- 保持现有的核心状态值不变
- 优化提示词，确保返回标准核心状态值

### 阶段 3: 更新 EpicDriver
- 添加状态值转换逻辑
- 在所有 `update_story_status()` 调用中使用正确的处理状态值

### 阶段 4: 更新 Dev/QA Agent
- 基于核心状态值进行业务逻辑判断
- 保持现有的判断逻辑不变

### 阶段 5: 测试验证
- 运行完整的端到端测试
- 验证状态流转的正确性

## 总结

通过统一标准状态值，我们实现了：

1. **一致性**: 所有组件使用相同的状态值标准
2. **可理解性**: 核心状态值直观易懂
3. **可维护性**: 清晰的状态流转逻辑
4. **可扩展性**: 易于添加新的状态值

**关键原则**: 核心状态值用于文档和显示，处理状态值用于数据库和内部跟踪。
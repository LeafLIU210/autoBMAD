# BasedPyright 检查报告
**生成时间**: 2026-01-07 07:27:10
**检查时间**: 2026-01-07T07:27:10.058226
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 16 |
| ❌ 错误 (Error) | 12 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.04 秒 |

## 🔴 错误详情

共发现 **12** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py`: 8 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py`: 4 个错误

### 按规则分组

- `reportUnknownMemberType`: 4 次
- `reportAttributeAccessIssue`: 3 次
- `reportUnusedImport`: 2 次
- `reportUnknownVariableType`: 1 次
- `reportArgumentType`: 1 次
- `reportUnknownArgumentType`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:12

- **规则**: `reportUnusedImport`
- **位置**: 第 12 行, 第 34 列
- **错误信息**: "cast" 导入项未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:12

- **规则**: `reportUnusedImport`
- **位置**: 第 12 行, 第 40 列
- **错误信息**: "Awaitable" 导入项未使用

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:465

- **规则**: `reportUnknownVariableType`
- **位置**: 第 465 行, 第 24 列
- **错误信息**: "close_task" 的类型部分未知
  "close_task" 为 "Task[Unknown]" 类型

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:465

- **规则**: `reportArgumentType`
- **位置**: 第 465 行, 第 57 列
- **错误信息**: "object" 类型的实参无法赋值给函数 "create_task" 中 "_CoroutineLike[_T@create_task]" 类型的形参 "coro"
  "object" 类型与 "_CoroutineLike[_T@create_task]" 类型不兼容
    "object" 与 "Coroutine[Any, Any, _T@create_task]" 不兼容
    "object" 与 Protocol 类 "Generator[Any, None, _T@create_task]" 不兼容
      "__next__" 不存在
      "send" 不存在
      "throw" 不存在
      "close" 不存在
      "__iter__" 不存在

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:467

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 467 行, 第 51 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "wait_for" 函数中的 "fut" 形参
  参数类型为 "Task[Unknown]"

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:484

- **规则**: `reportUnknownMemberType`
- **位置**: 第 484 行, 第 12 列
- **错误信息**: "_stop_event" 类型未知

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:484

- **规则**: `reportUnknownMemberType`
- **位置**: 第 484 行, 第 12 列
- **错误信息**: "set" 类型未知

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:484

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 484 行, 第 17 列
- **错误信息**: 无法访问 "SafeClaudeSDK*" 类的 "_stop_event" 属性
  属性 "_stop_event" 未知

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:206

- **规则**: `reportUnknownMemberType`
- **位置**: 第 206 行, 第 23 列
- **错误信息**: "timeout" 类型未知

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:206

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 206 行, 第 31 列
- **错误信息**: "timeout" 不是 "asyncio" 模块的已知属性

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:1092

- **规则**: `reportUnknownMemberType`
- **位置**: 第 1092 行, 第 23 列
- **错误信息**: "timeout" 类型未知

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:1092

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 1092 行, 第 31 列
- **错误信息**: "timeout" 不是 "asyncio" 模块的已知属性

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\agents.py`
3. `..\autoBMAD\epic_automation\code_quality_agent.py`
4. `..\autoBMAD\epic_automation\dev_agent.py`
5. `..\autoBMAD\epic_automation\epic_driver.py`
6. `..\autoBMAD\epic_automation\init_db.py`
7. `..\autoBMAD\epic_automation\log_manager.py`
8. `..\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py`
9. `..\autoBMAD\epic_automation\qa_agent.py`
10. `..\autoBMAD\epic_automation\qa_tools_integration.py`
11. `..\autoBMAD\epic_automation\sdk_session_manager.py`
12. `..\autoBMAD\epic_automation\sdk_wrapper.py`
13. `..\autoBMAD\epic_automation\sm_agent.py`
14. `..\autoBMAD\epic_automation\state_manager.py`
15. `..\autoBMAD\epic_automation\test_automation_agent.py`
16. `..\autoBMAD\epic_automation\test_logging.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:12:35 - error: "cast" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:12:41 - error: "Awaitable" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:465:25 - error: "close_task" 的类型部分未知
    "close_task" 为 "Task[Unknown]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:465:58 - error: "object" 类型的实参无法赋值给函数 "create_task" 中 "_CoroutineLike[_T@create_task]" 类型的形参 "coro"
    "object" 类型与 "_CoroutineLike[_T@create_task]" 类型不兼容
      "object" 与 "Coroutine[Any, Any, _T@create_task]" 不兼容
      "object" 与 Protocol 类 "Generator[Any, None, _T@create_task]" 不兼容
        "__next__" 不存在
        "send" 不存在
        "throw" 不存在
        "close" 不存在
        "__iter__" 不存在 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:467:52 - error: 部分参数的类型未知
    实参对应于 "wait_for" 函数中的 "fut" 形参
    参数类型为 "Task[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:484:13 - error: "_stop_event" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:484:13 - error: "set" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:484:18 - error: 无法访问 "SafeClaudeSDK*" 类的 "_stop_event" 属性
    属性 "_stop_event" 未知 (reportAttributeAccessIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:206:24 - error: "timeout" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:206:32 - error: "timeout" 不是 "asyncio" 模块的已知属性 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:1092:24 - error: "timeout" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:1092:32 - error: "timeout" 不是 "asyncio" 模块的已知属性 (reportAttributeAccessIssue)
12 errors, 0 warnings, 0 notes
```


# BasedPyright 检查报告
**生成时间**: 2026-01-06 06:23:47
**检查时间**: 2026-01-06T06:23:46.931156
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 11 |
| ❌ 错误 (Error) | 43 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.65 秒 |

## 🔴 错误详情

共发现 **43** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py`: 34 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py`: 5 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py`: 4 个错误

### 按规则分组

- `reportAttributeAccessIssue`: 16 次
- `reportUnknownMemberType`: 9 次
- `reportUndefinedVariable`: 3 次
- `reportUnknownVariableType`: 3 次
- `reportUnknownArgumentType`: 3 次
- `reportUnknownParameterType`: 2 次
- `reportInvalidTypeForm`: 2 次
- `reportGeneralTypeIssues`: 2 次
- `reportArgumentType`: 2 次
- `reportOptionalCall`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:358

- **规则**: `reportUndefinedVariable`
- **位置**: 第 358 行, 第 15 列
- **错误信息**: "query" 未定义

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:358

- **规则**: `reportUndefinedVariable`
- **位置**: 第 358 行, 第 37 列
- **错误信息**: "ClaudeAgentOptions" 未定义

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:359

- **规则**: `reportUnknownVariableType`
- **位置**: 第 359 行, 第 16 列
- **错误信息**: "options" 类型未知

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:359

- **规则**: `reportUndefinedVariable`
- **位置**: 第 359 行, 第 26 列
- **错误信息**: "ClaudeAgentOptions" 未定义

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:364

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 364 行, 第 44 列
- **错误信息**: 参数类型未知
  实参对应于 "__init__" 函数中的 "options" 形参

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:535

- **规则**: `reportUnknownMemberType`
- **位置**: 第 535 行, 第 8 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:540

- **规则**: `reportUnknownMemberType`
- **位置**: 第 540 行, 第 8 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:548

- **规则**: `reportUnknownVariableType`
- **位置**: 第 548 行, 第 12 列
- **错误信息**: "task" 类型未知

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:549

- **规则**: `reportUnknownMemberType`
- **位置**: 第 549 行, 第 19 列
- **错误信息**: "done" 类型未知

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:38

- **规则**: `reportUnknownParameterType`
- **位置**: 第 38 行, 第 36 列
- **错误信息**: "options" 参数的类型未知

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:38

- **规则**: `reportInvalidTypeForm`
- **位置**: 第 38 行, 第 45 列
- **错误信息**: 类型表达式中不允许使用变量

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:40

- **规则**: `reportUnknownMemberType`
- **位置**: 第 40 行, 第 8 列
- **错误信息**: "options" 类型未知

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:81

- **规则**: `reportOptionalCall`
- **位置**: 第 81 行, 第 24 列
- **错误信息**: `None` 不支持调用

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:81

- **规则**: `reportUnknownMemberType`
- **位置**: 第 81 行, 第 58 列
- **错误信息**: "options" 类型未知

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:81

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 81 行, 第 58 列
- **错误信息**: 参数类型未知
  实参对应于 "query" 函数中的 "options" 形参

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:84

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 84 行, 第 23 列
- **错误信息**: "AsyncIterator[Message]" 类型的对象不能用于 `async with` 语句，因为它未实现 "__aenter__"
  属性 "__aenter__" 未知

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:84

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 84 行, 第 23 列
- **错误信息**: "AsyncIterator[Message]" 类型的对象不能用于 `with` 语句，因为它未实现 "__aexit__"
  属性 "__aexit__" 未知

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:88

- **规则**: `reportArgumentType`
- **位置**: 第 88 行, 第 43 列
- **错误信息**: "type[ResultMessage] | None" 类型的实参无法赋值给函数 "isinstance" 中 "_ClassInfo" 类型的形参 "class_or_tuple"
  "type[ResultMessage] | None" 类型与 "_ClassInfo" 类型不兼容
    "None" 类型与 "_ClassInfo" 类型不兼容
      "None" 与 "type" 不兼容
      "None" 与 "tuple[_ClassInfo, ...]" 不兼容

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:88

- **规则**: `reportArgumentType`
- **位置**: 第 88 行, 第 43 列
- **错误信息**: `isinstance` 的第二个参数必须是单个类或由多个类构成的元组
  `None` 不能参与 `isinstance()` 或 `issubclass()`

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:89

- **规则**: `reportUnknownMemberType`
- **位置**: 第 89 行, 第 27 列
- **错误信息**: "is_error" 的类型部分未知
  "is_error" 为 "Unknown | bool" 类型

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:89

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 89 行, 第 35 列
- **错误信息**: 无法访问 "UserMessage" 类的 "is_error" 属性
  属性 "is_error" 未知

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:89

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 89 行, 第 35 列
- **错误信息**: 无法访问 "AssistantMessage" 类的 "is_error" 属性
  属性 "is_error" 未知

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:89

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 89 行, 第 35 列
- **错误信息**: 无法访问 "SystemMessage" 类的 "is_error" 属性
  属性 "is_error" 未知

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:89

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 89 行, 第 35 列
- **错误信息**: 无法访问 "StreamEvent" 类的 "is_error" 属性
  属性 "is_error" 未知

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:90

- **规则**: `reportUnknownMemberType`
- **位置**: 第 90 行, 第 62 列
- **错误信息**: "result" 的类型部分未知
  "result" 为 "Unknown | str | None" 类型

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:90

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 90 行, 第 70 列
- **错误信息**: 无法访问 "UserMessage" 类的 "result" 属性
  属性 "result" 未知

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:90

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 90 行, 第 70 列
- **错误信息**: 无法访问 "AssistantMessage" 类的 "result" 属性
  属性 "result" 未知

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:90

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 90 行, 第 70 列
- **错误信息**: 无法访问 "SystemMessage" 类的 "result" 属性
  属性 "result" 未知

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:90

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 90 行, 第 70 列
- **错误信息**: 无法访问 "StreamEvent" 类的 "result" 属性
  属性 "result" 未知

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93

- **规则**: `reportUnknownVariableType`
- **位置**: 第 93 行, 第 28 列
- **错误信息**: "result_preview" 的类型部分未知
  "result_preview" 为 "Unknown | str" 类型

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93

- **规则**: `reportUnknownMemberType`
- **位置**: 第 93 行, 第 45 列
- **错误信息**: "result" 的类型部分未知
  "result" 为 "Unknown | str" 类型

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 93 行, 第 53 列
- **错误信息**: 无法访问 "UserMessage" 类的 "result" 属性
  属性 "result" 未知

#### 33. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 93 行, 第 53 列
- **错误信息**: 无法访问 "AssistantMessage" 类的 "result" 属性
  属性 "result" 未知

#### 34. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 93 行, 第 53 列
- **错误信息**: 无法访问 "SystemMessage" 类的 "result" 属性
  属性 "result" 未知

#### 35. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 93 行, 第 53 列
- **错误信息**: 无法访问 "StreamEvent" 类的 "result" 属性
  属性 "result" 未知

#### 36. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93

- **规则**: `reportUnknownMemberType`
- **位置**: 第 93 行, 第 69 列
- **错误信息**: "result" 的类型部分未知
  "result" 为 "Unknown | str | None" 类型

#### 37. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 93 行, 第 77 列
- **错误信息**: 无法访问 "UserMessage" 类的 "result" 属性
  属性 "result" 未知

#### 38. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 93 行, 第 77 列
- **错误信息**: 无法访问 "AssistantMessage" 类的 "result" 属性
  属性 "result" 未知

#### 39. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 93 行, 第 77 列
- **错误信息**: 无法访问 "SystemMessage" 类的 "result" 属性
  属性 "result" 未知

#### 40. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 93 行, 第 77 列
- **错误信息**: 无法访问 "StreamEvent" 类的 "result" 属性
  属性 "result" 未知

#### 41. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:134

- **规则**: `reportUnknownParameterType`
- **位置**: 第 134 行, 第 4 列
- **错误信息**: "options" 参数的类型未知

#### 42. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:134

- **规则**: `reportInvalidTypeForm`
- **位置**: 第 134 行, 第 13 列
- **错误信息**: 类型表达式中不允许使用变量

#### 43. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:144

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 144 行, 第 32 列
- **错误信息**: 参数类型未知
  实参对应于 "__init__" 函数中的 "options" 形参

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\code_quality_agent.py`
3. `..\autoBMAD\epic_automation\dev_agent.py`
4. `..\autoBMAD\epic_automation\epic_driver.py`
5. `..\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py`
6. `..\autoBMAD\epic_automation\qa_agent.py`
7. `..\autoBMAD\epic_automation\qa_tools_integration.py`
8. `..\autoBMAD\epic_automation\sdk_wrapper.py`
9. `..\autoBMAD\epic_automation\sm_agent.py`
10. `..\autoBMAD\epic_automation\state_manager.py`
11. `..\autoBMAD\epic_automation\test_automation_agent.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:358:16 - error: "query" 未定义 (reportUndefinedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:358:38 - error: "ClaudeAgentOptions" 未定义 (reportUndefinedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:359:17 - error: "options" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:359:27 - error: "ClaudeAgentOptions" 未定义 (reportUndefinedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:364:45 - error: 参数类型未知
    实参对应于 "__init__" 函数中的 "options" 形参 (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:535:9 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:540:9 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:548:13 - error: "task" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:549:20 - error: "done" 类型未知 (reportUnknownMemberType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:38:37 - error: "options" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:38:46 - error: 类型表达式中不允许使用变量 (reportInvalidTypeForm)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:40:9 - error: "options" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:81:25 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:81:59 - error: "options" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:81:59 - error: 参数类型未知
    实参对应于 "query" 函数中的 "options" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:84:24 - error: "AsyncIterator[Message]" 类型的对象不能用于 `async with` 语句，因为它未实现 "__aenter__"
    属性 "__aenter__" 未知 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:84:24 - error: "AsyncIterator[Message]" 类型的对象不能用于 `with` 语句，因为它未实现 "__aexit__"
    属性 "__aexit__" 未知 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:88:44 - error: "type[ResultMessage] | None" 类型的实参无法赋值给函数 "isinstance" 中 "_ClassInfo" 类型的形参 "class_or_tuple"
    "type[ResultMessage] | None" 类型与 "_ClassInfo" 类型不兼容
      "None" 类型与 "_ClassInfo" 类型不兼容
        "None" 与 "type" 不兼容
        "None" 与 "tuple[_ClassInfo, ...]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:88:44 - error: `isinstance` 的第二个参数必须是单个类或由多个类构成的元组
    `None` 不能参与 `isinstance()` 或 `issubclass()` (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:89:28 - error: "is_error" 的类型部分未知
    "is_error" 为 "Unknown | bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:89:36 - error: 无法访问 "UserMessage" 类的 "is_error" 属性
    属性 "is_error" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:89:36 - error: 无法访问 "AssistantMessage" 类的 "is_error" 属性
    属性 "is_error" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:89:36 - error: 无法访问 "SystemMessage" 类的 "is_error" 属性
    属性 "is_error" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:89:36 - error: 无法访问 "StreamEvent" 类的 "is_error" 属性
    属性 "is_error" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:90:63 - error: "result" 的类型部分未知
    "result" 为 "Unknown | str | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:90:71 - error: 无法访问 "UserMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:90:71 - error: 无法访问 "AssistantMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:90:71 - error: 无法访问 "SystemMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:90:71 - error: 无法访问 "StreamEvent" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93:29 - error: "result_preview" 的类型部分未知
    "result_preview" 为 "Unknown | str" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93:46 - error: "result" 的类型部分未知
    "result" 为 "Unknown | str" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93:54 - error: 无法访问 "UserMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93:54 - error: 无法访问 "AssistantMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93:54 - error: 无法访问 "SystemMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93:54 - error: 无法访问 "StreamEvent" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93:70 - error: "result" 的类型部分未知
    "result" 为 "Unknown | str | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93:78 - error: 无法访问 "UserMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93:78 - error: 无法访问 "AssistantMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93:78 - error: 无法访问 "SystemMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:93:78 - error: 无法访问 "StreamEvent" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:134:5 - error: "options" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:134:14 - error: 类型表达式中不允许使用变量 (reportInvalidTypeForm)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:144:33 - error: 参数类型未知
    实参对应于 "__init__" 函数中的 "options" 形参 (reportUnknownArgumentType)
43 errors, 0 warnings, 0 notes
```


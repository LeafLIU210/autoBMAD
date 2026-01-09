# BasedPyright 检查报告
**生成时间**: 2026-01-06 20:56:11
**检查时间**: 2026-01-06T20:56:10.811912
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 16 |
| ❌ 错误 (Error) | 45 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.03 秒 |

## 🔴 错误详情

共发现 **45** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 21 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py`: 11 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py`: 4 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py`: 1 个错误

### 按规则分组

- `reportUnknownMemberType`: 11 次
- `reportUnknownArgumentType`: 10 次
- `reportUnusedImport`: 7 次
- `reportPossiblyUnboundVariable`: 4 次
- `reportUnknownLambdaType`: 4 次
- `reportOptionalCall`: 3 次
- `reportUnknownVariableType`: 2 次
- `reportIndexIssue`: 2 次
- `reportUnusedVariable`: 1 次
- `reportArgumentType`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:259

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 259 行, 第 54 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__init__" 函数中的 "o" 形参
  参数类型为 "Unknown | type[ClaudeSDKClient] | None"

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:284

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 284 行, 第 63 列
- **错误信息**: 参数类型未知
  实参对应于 "dir" 函数中的 "o" 形参

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:311

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 311 行, 第 27 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:313

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 313 行, 第 89 列
- **错误信息**: 参数类型未知
  实参对应于 "dir" 函数中的 "o" 形参

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:17

- **规则**: `reportUnusedImport`
- **位置**: 第 17 行, 第 60 列
- **错误信息**: "ResultMessage" 导入项未使用

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:29

- **规则**: `reportUnusedImport`
- **位置**: 第 29 行, 第 54 列
- **错误信息**: "SDKExecutionResult" 导入项未使用

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:497

- **规则**: `reportOptionalCall`
- **位置**: 第 497 行, 第 22 列
- **错误信息**: `None` 不支持调用

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:717

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 717 行, 第 63 列
- **错误信息**: "story_path" 可能未绑定

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:743

- **规则**: `reportUnknownMemberType`
- **位置**: 第 743 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:745

- **规则**: `reportUnknownMemberType`
- **位置**: 第 745 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:749

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 749 行, 第 63 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:749

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 749 行, 第 94 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:792

- **规则**: `reportUnknownVariableType`
- **位置**: 第 792 行, 第 12 列
- **错误信息**: "essential_elements" 的类型部分未知
  "essential_elements" 为 "list[tuple[str, (c: Unknown) -> (Unknown | Literal[True])] | tuple[str, (c: Unknown) -> bool]]" 类型

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:793

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 793 行, 第 43 列
- **错误信息**: "c" 参数的类型未知

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:793

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 793 行, 第 46 列
- **错误信息**: 该 `lambda` 的返回类型 "Unknown | Literal[True]" 部分未知

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:793

- **规则**: `reportUnknownMemberType`
- **位置**: 第 793 行, 第 58 列
- **错误信息**: "strip" 类型未知

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:793

- **规则**: `reportUnknownMemberType`
- **位置**: 第 793 行, 第 58 列
- **错误信息**: "startswith" 类型未知

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:794

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 794 行, 第 34 列
- **错误信息**: "c" 参数的类型未知

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:794

- **规则**: `reportUnknownMemberType`
- **位置**: 第 794 行, 第 49 列
- **错误信息**: "lower" 类型未知

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:795

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 795 行, 第 41 列
- **错误信息**: "c" 参数的类型未知

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:795

- **规则**: `reportUnknownMemberType`
- **位置**: 第 795 行, 第 48 列
- **错误信息**: "split" 类型未知

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:795

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 795 行, 第 48 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:799

- **规则**: `reportUnknownVariableType`
- **位置**: 第 799 行, 第 30 列
- **错误信息**: "check_func" 的类型部分未知
  "check_func" 为 "((c: Unknown) -> (Unknown | Literal[True])) | ((c: Unknown) -> bool)" 类型

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:801

- **规则**: `reportUnknownMemberType`
- **位置**: 第 801 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:807

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 807 行, 第 23 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:827

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 827 行, 第 66 列
- **错误信息**: "story_path" 可能未绑定

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:856

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 856 行, 第 61 列
- **错误信息**: "story_path" 可能未绑定

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:882

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 882 行, 第 71 列
- **错误信息**: "story_path" 可能未绑定

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:14

- **规则**: `reportUnusedImport`
- **位置**: 第 14 行, 第 34 列
- **错误信息**: "Callable" 导入项未使用

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:23

- **规则**: `reportUnusedImport`
- **位置**: 第 23 行, 第 54 列
- **错误信息**: "SDKExecutionResult" 导入项未使用

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:27

- **规则**: `reportUnusedImport`
- **位置**: 第 27 行, 第 33 列
- **错误信息**: "query" 导入项未使用

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:27

- **规则**: `reportUnusedImport`
- **位置**: 第 27 行, 第 60 列
- **错误信息**: "ResultMessage" 导入项未使用

#### 33. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:266

- **规则**: `reportOptionalCall`
- **位置**: 第 266 行, 第 26 列
- **错误信息**: `None` 不支持调用

#### 34. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:329

- **规则**: `reportUnknownMemberType`
- **位置**: 第 329 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 35. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:333

- **规则**: `reportUnknownMemberType`
- **位置**: 第 333 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 36. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:345

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 345 行, 第 70 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "join" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

#### 37. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:404

- **规则**: `reportUnknownMemberType`
- **位置**: 第 404 行, 第 24 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 38. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:407

- **规则**: `reportUnknownMemberType`
- **位置**: 第 407 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 39. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:414

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 414 行, 第 52 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 40. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:171

- **规则**: `reportUnusedVariable`
- **位置**: 第 171 行, 第 54 列
- **错误信息**: 变量 "context" 未使用

#### 41. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:239

- **规则**: `reportIndexIssue`
- **位置**: 第 239 行, 第 37 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 42. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:247

- **规则**: `reportIndexIssue`
- **位置**: 第 247 行, 第 32 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 43. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:524

- **规则**: `reportArgumentType`
- **位置**: 第 524 行, 第 51 列
- **错误信息**: "object" 类型的实参无法赋值给函数 "wait_for" 中 "_FutureLike[_T@wait_for]" 类型的形参 "fut"
  "object" 类型与 "_FutureLike[_T@wait_for]" 类型不兼容
    "object" 与 Protocol 类 "Awaitable[_T@wait_for]" 不兼容
      "__await__" 不存在
    "object" 与 "Future[_T@wait_for]" 不兼容
    "object" 与 Protocol 类 "Generator[Any, None, _T@wait_for]" 不兼容
      "__next__" 不存在
      "send" 不存在
      "throw" 不存在
  ...

#### 44. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:19

- **规则**: `reportUnusedImport`
- **位置**: 第 19 行, 第 54 列
- **错误信息**: "SDKExecutionResult" 导入项未使用

#### 45. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:520

- **规则**: `reportOptionalCall`
- **位置**: 第 520 行, 第 22 列
- **错误信息**: `None` 不支持调用

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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:259:55 - error: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "o" 形参
    参数类型为 "Unknown | type[ClaudeSDKClient] | None" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:284:64 - error: 参数类型未知
    实参对应于 "dir" 函数中的 "o" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:311:28 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:313:90 - error: 参数类型未知
    实参对应于 "dir" 函数中的 "o" 形参 (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:17:61 - error: "ResultMessage" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:29:55 - error: "SDKExecutionResult" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:497:23 - error: `None` 不支持调用 (reportOptionalCall)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:717:64 - error: "story_path" 可能未绑定 (reportPossiblyUnboundVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:743:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:745:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:749:64 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:749:95 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:792:13 - error: "essential_elements" 的类型部分未知
    "essential_elements" 为 "list[tuple[str, (c: Unknown) -> (Unknown | Literal[True])] | tuple[str, (c: Unknown) -> bool]]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:793:44 - error: "c" 参数的类型未知 (reportUnknownLambdaType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:793:47 - error: 该 `lambda` 的返回类型 "Unknown | Literal[True]" 部分未知 (reportUnknownLambdaType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:793:59 - error: "strip" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:793:59 - error: "startswith" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:794:35 - error: "c" 参数的类型未知 (reportUnknownLambdaType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:794:50 - error: "lower" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:795:42 - error: "c" 参数的类型未知 (reportUnknownLambdaType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:795:49 - error: "split" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:795:49 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:799:31 - error: "check_func" 的类型部分未知
    "check_func" 为 "((c: Unknown) -> (Unknown | Literal[True])) | ((c: Unknown) -> bool)" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:801:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:807:24 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:827:67 - error: "story_path" 可能未绑定 (reportPossiblyUnboundVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:856:62 - error: "story_path" 可能未绑定 (reportPossiblyUnboundVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:882:72 - error: "story_path" 可能未绑定 (reportPossiblyUnboundVariable)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:14:35 - error: "Callable" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:23:55 - error: "SDKExecutionResult" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:27:34 - error: "query" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:27:61 - error: "ResultMessage" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:266:27 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:329:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:333:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:345:71 - error: 部分参数的类型未知
    实参对应于 "join" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:404:25 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:407:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:414:53 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:171:55 - error: 变量 "context" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:239:38 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:247:33 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:524:52 - error: "object" 类型的实参无法赋值给函数 "wait_for" 中 "_FutureLike[_T@wait_for]" 类型的形参 "fut"
    "object" 类型与 "_FutureLike[_T@wait_for]" 类型不兼容
      "object" 与 Protocol 类 "Awaitable[_T@wait_for]" 不兼容
        "__await__" 不存在
      "object" 与 "Future[_T@wait_for]" 不兼容
      "object" 与 Protocol 类 "Generator[Any, None, _T@wait_for]" 不兼容
        "__next__" 不存在
        "send" 不存在
        "throw" 不存在
    ... (reportArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:19:55 - error: "SDKExecutionResult" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:520:23 - error: `None` 不支持调用 (reportOptionalCall)
45 errors, 0 warnings, 0 notes
```


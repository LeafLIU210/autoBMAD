# BasedPyright 检查报告
**生成时间**: 2026-01-07 10:38:54
**检查时间**: 2026-01-07T10:38:52.603341
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 16 |
| ❌ 错误 (Error) | 73 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.01 秒 |

## 🔴 错误详情

共发现 **73** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py`: 30 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py`: 18 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py`: 13 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py`: 8 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py`: 4 个错误

### 按规则分组

- `reportInvalidStringEscapeSequence`: 16 次
- `reportUnknownMemberType`: 15 次
- `reportUnknownVariableType`: 10 次
- `reportUnusedImport`: 7 次
- `reportOperatorIssue`: 4 次
- `reportAttributeAccessIssue`: 2 次
- `reportGeneralTypeIssues`: 2 次
- `reportArgumentType`: 2 次
- `reportPossiblyUnboundVariable`: 2 次
- `reportUnknownParameterType`: 2 次
- `reportUnknownArgumentType`: 2 次
- `reportMissingTypeArgument`: 2 次
- `reportUnusedVariable`: 2 次
- `reportReturnType`: 1 次
- `reportAssignmentType`: 1 次
- `reportMissingParameterType`: 1 次
- `reportUndefinedVariable`: 1 次
- `reportIndexIssue`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:185

- **规则**: `reportUnknownMemberType`
- **位置**: 第 185 行, 第 26 列
- **错误信息**: "add_quality_phase_record" 类型未知

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:185

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 185 行, 第 45 列
- **错误信息**: 无法访问 "StateManager" 类的 "add_quality_phase_record" 属性
  属性 "add_quality_phase_record" 未知

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:228

- **规则**: `reportUnknownMemberType`
- **位置**: 第 228 行, 第 26 列
- **错误信息**: "add_quality_phase_record" 类型未知

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:228

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 228 行, 第 45 列
- **错误信息**: 无法访问 "StateManager" 类的 "add_quality_phase_record" 属性
  属性 "add_quality_phase_record" 未知

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 8 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 15 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 39 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 55 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:23

- **规则**: `reportUnusedImport`
- **位置**: 第 23 行, 第 7 列
- **错误信息**: "time" 导入项未使用

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:24

- **规则**: `reportUnusedImport`
- **位置**: 第 24 行, 第 21 列
- **错误信息**: "datetime" 导入项未使用

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:30

- **规则**: `reportUnusedImport`
- **位置**: 第 30 行, 第 52 列
- **错误信息**: "SDKErrorType" 导入项未使用

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:215

- **规则**: `reportReturnType`
- **位置**: 第 215 行, 第 15 列
- **错误信息**: "dict[str, bool | list[str] | str | int]" 类型不匹配返回类型 "dict[str, str | bool | list[str]]"
  "Literal[0]" 类型与 "str | bool | list[str]" 类型不兼容
    "Literal[0]" 与 "str" 不兼容
    "Literal[0]" 与 "bool" 不兼容
    "Literal[0]" 与 "list[str]" 不兼容
  "Literal[0]" 类型与 "str | bool | list[str]" 类型不兼容
    "Literal[0]" 与 "str" 不兼容
    "Literal[0]" 与 "bool" 不兼容
    "Literal[0]" 与 "list[str]" 不兼容

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 8 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 15 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 39 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 55 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:230

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 230 行, 第 23 列
- **错误信息**: "IsolatedSDKContext" 类型的对象不能用于 `with` 语句，因为它未实现 "__aexit__"
  属性 "__aexit__" 未知

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:255

- **规则**: `reportAssignmentType`
- **位置**: 第 255 行, 第 22 列
- **错误信息**: "int | float" 类型不匹配声明的 "int | None" 类型
  "int | float" 类型与 "int | None" 类型不兼容
    "float" 类型与 "int | None" 类型不兼容
      "float" 与 "int" 不兼容
      "float" 与 "None" 不兼容

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:259

- **规则**: `reportOperatorIssue`
- **位置**: 第 259 行, 第 14 列
- **错误信息**: "int" 与 "int | None" 类型不支持 "<=" 运算符
  "int" 与 "None" 类型不支持 "<=" 运算符

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:312

- **规则**: `reportOperatorIssue`
- **位置**: 第 312 行, 第 51 列
- **错误信息**: "int" 与 "int | None" 类型不支持 "<" 运算符
  "int" 与 "None" 类型不支持 "<" 运算符

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:340

- **规则**: `reportArgumentType`
- **位置**: 第 340 行, 第 31 列
- **错误信息**: "CancelledError" 类型的实参无法赋值给函数 "__init__" 中 "Exception | None" 类型的形参 "last_error"
  "CancelledError" 类型与 "Exception | None" 类型不兼容
    "CancelledError" 与 "Exception" 不兼容
    "CancelledError" 与 "None" 不兼容

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:383

- **规则**: `reportOperatorIssue`
- **位置**: 第 383 行, 第 51 列
- **错误信息**: "int" 与 "int | None" 类型不支持 "<" 运算符
  "int" 与 "None" 类型不支持 "<" 运算符

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:412

- **规则**: `reportOperatorIssue`
- **位置**: 第 412 行, 第 51 列
- **错误信息**: "int" 与 "int | None" 类型不支持 "<" 运算符
  "int" 与 "None" 类型不支持 "<" 运算符

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:431

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 431 行, 第 43 列
- **错误信息**: "start_time" 可能未绑定

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:432

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 432 行, 第 23 列
- **错误信息**: "session_id" 可能未绑定

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 8 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 15 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 39 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 55 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:16

- **规则**: `reportUnusedImport`
- **位置**: 第 16 行, 第 7 列
- **错误信息**: "sys" 导入项未使用

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:20

- **规则**: `reportUnusedImport`
- **位置**: 第 20 行, 第 23 列
- **错误信息**: "asynccontextmanager" 导入项未使用

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:85

- **规则**: `reportUnknownParameterType`
- **位置**: 第 85 行, 第 23 列
- **错误信息**: "generator" 参数的类型未知

#### 33. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:85

- **规则**: `reportMissingParameterType`
- **位置**: 第 85 行, 第 23 列
- **错误信息**: "generator" 参数缺少类型注解

#### 34. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:86

- **规则**: `reportUnknownMemberType`
- **位置**: 第 86 行, 第 8 列
- **错误信息**: "generator" 类型未知

#### 35. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:94

- **规则**: `reportUnknownParameterType`
- **位置**: 第 94 行, 第 14 列
- **错误信息**: 返回类型未知

#### 36. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:100

- **规则**: `reportUnknownVariableType`
- **位置**: 第 100 行, 第 19 列
- **错误信息**: 返回类型未知

#### 37. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:100

- **规则**: `reportUnknownMemberType`
- **位置**: 第 100 行, 第 25 列
- **错误信息**: "generator" 类型未知

#### 38. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:100

- **规则**: `reportUnknownMemberType`
- **位置**: 第 100 行, 第 25 列
- **错误信息**: "__anext__" 类型未知

#### 39. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:118

- **规则**: `reportUnknownMemberType`
- **位置**: 第 118 行, 第 29 列
- **错误信息**: "generator" 类型未知

#### 40. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:118

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 118 行, 第 29 列
- **错误信息**: 参数类型未知
  实参对应于 "getattr" 函数中的 "o" 形参

#### 41. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:123

- **规则**: `reportArgumentType`
- **位置**: 第 123 行, 第 43 列
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

#### 42. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:485

- **规则**: `reportUnknownVariableType`
- **位置**: 第 485 行, 第 22 列
- **错误信息**: "message" 类型未知

#### 43. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:485

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 485 行, 第 33 列
- **错误信息**: "SafeAsyncGenerator" 不支持迭代
  "CoroutineType[Any, Any, SafeAsyncGenerator]" 类型上未定义 "__anext__" 方法

#### 44. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 8 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 45. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 15 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 46. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 39 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 47. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:5

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 5 行, 第 55 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 48. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:20

- **规则**: `reportUnusedImport`
- **位置**: 第 20 行, 第 7 列
- **错误信息**: "uuid" 导入项未使用

#### 49. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:21

- **规则**: `reportUnusedImport`
- **位置**: 第 21 行, 第 7 列
- **错误信息**: "weakref" 导入项未使用

#### 50. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:52

- **规则**: `reportUndefinedVariable`
- **位置**: 第 52 行, 第 27 列
- **错误信息**: "Dict" 未定义

#### 51. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:52

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 52 行, 第 37 列
- **错误信息**: "Task" 泛型类应有类型参数

#### 52. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:62

- **规则**: `reportUnusedVariable`
- **位置**: 第 62 行, 第 8 列
- **错误信息**: 变量 "task_id" 未使用

#### 53. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:63

- **规则**: `reportUnknownMemberType`
- **位置**: 第 63 行, 第 8 列
- **错误信息**: "lock_waiters" 类型未知

#### 54. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:74

- **规则**: `reportUnknownMemberType`
- **位置**: 第 74 行, 第 12 列
- **错误信息**: "lock_waiters" 类型未知

#### 55. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:74

- **规则**: `reportUnknownMemberType`
- **位置**: 第 74 行, 第 12 列
- **错误信息**: "pop" 类型未知

#### 56. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:82

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 82 行, 第 26 列
- **错误信息**: "Queue" 泛型类应有类型参数

#### 57. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:93

- **规则**: `reportUnknownMemberType`
- **位置**: 第 93 行, 第 18 列
- **错误信息**: "connections" 的类型部分未知
  "connections" 为 "Queue[Unknown]" 类型

#### 58. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:93

- **规则**: `reportUnknownMemberType`
- **位置**: 第 93 行, 第 18 列
- **错误信息**: "put" 的类型部分未知
  "put" 为 "(item: Unknown) -> CoroutineType[Any, Any, None]" 类型

#### 59. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:98

- **规则**: `reportUnknownVariableType`
- **位置**: 第 98 行, 第 12 列
- **错误信息**: "conn" 类型未知

#### 60. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:98

- **规则**: `reportUnknownMemberType`
- **位置**: 第 98 行, 第 42 列
- **错误信息**: "connections" 的类型部分未知
  "connections" 为 "Queue[Unknown]" 类型

#### 61. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:98

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 98 行, 第 42 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "wait_for" 函数中的 "fut" 形参
  参数类型为 "CoroutineType[Any, Any, Unknown]"

#### 62. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:99

- **规则**: `reportUnknownVariableType`
- **位置**: 第 99 行, 第 19 列
- **错误信息**: 返回类型未知

#### 63. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:106

- **规则**: `reportUnknownMemberType`
- **位置**: 第 106 行, 第 18 列
- **错误信息**: "connections" 的类型部分未知
  "connections" 为 "Queue[Unknown]" 类型

#### 64. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:106

- **规则**: `reportUnknownMemberType`
- **位置**: 第 106 行, 第 18 列
- **错误信息**: "put" 的类型部分未知
  "put" 为 "(item: Unknown) -> CoroutineType[Any, Any, None]" 类型

#### 65. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:313

- **规则**: `reportUnusedVariable`
- **位置**: 第 313 行, 第 16 列
- **错误信息**: 变量 "story_id" 未使用

#### 66. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:373

- **规则**: `reportUnknownVariableType`
- **位置**: 第 373 行, 第 27 列
- **错误信息**: 返回类型 "dict[Unknown, Any]" 部分未知

#### 67. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:373

- **规则**: `reportUnknownVariableType`
- **位置**: 第 373 行, 第 53 列
- **错误信息**: "k" 类型未知

#### 68. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:373

- **规则**: `reportUnknownVariableType`
- **位置**: 第 373 行, 第 56 列
- **错误信息**: "v" 类型未知

#### 69. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:375

- **规则**: `reportUnknownVariableType`
- **位置**: 第 375 行, 第 50 列
- **错误信息**: "v" 类型未知

#### 70. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:517

- **规则**: `reportUnknownMemberType`
- **位置**: 第 517 行, 第 24 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 71. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:519

- **规则**: `reportUnknownVariableType`
- **位置**: 第 519 行, 第 27 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 72. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:549

- **规则**: `reportUnknownVariableType`
- **位置**: 第 549 行, 第 27 列
- **错误信息**: 返回类型 "dict[Unknown, Unknown]" 部分未知

#### 73. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:627

- **规则**: `reportIndexIssue`
- **位置**: 第 627 行, 第 35 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

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
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:185:27 - error: "add_quality_phase_record" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:185:46 - error: 无法访问 "StateManager" 类的 "add_quality_phase_record" 属性
    属性 "add_quality_phase_record" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:228:27 - error: "add_quality_phase_record" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:228:46 - error: 无法访问 "StateManager" 类的 "add_quality_phase_record" 属性
    属性 "add_quality_phase_record" 未知 (reportAttributeAccessIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:5:9 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:5:16 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:5:40 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:5:56 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:23:8 - error: "time" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:24:22 - error: "datetime" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:30:53 - error: "SDKErrorType" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:215:16 - error: "dict[str, bool | list[str] | str | int]" 类型不匹配返回类型 "dict[str, str | bool | list[str]]"
    "Literal[0]" 类型与 "str | bool | list[str]" 类型不兼容
      "Literal[0]" 与 "str" 不兼容
      "Literal[0]" 与 "bool" 不兼容
      "Literal[0]" 与 "list[str]" 不兼容
    "Literal[0]" 类型与 "str | bool | list[str]" 类型不兼容
      "Literal[0]" 与 "str" 不兼容
      "Literal[0]" 与 "bool" 不兼容
      "Literal[0]" 与 "list[str]" 不兼容 (reportReturnType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:5:9 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:5:16 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:5:40 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:5:56 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:230:24 - error: "IsolatedSDKContext" 类型的对象不能用于 `with` 语句，因为它未实现 "__aexit__"
    属性 "__aexit__" 未知 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:255:23 - error: "int | float" 类型不匹配声明的 "int | None" 类型
    "int | float" 类型与 "int | None" 类型不兼容
      "float" 类型与 "int | None" 类型不兼容
        "float" 与 "int" 不兼容
        "float" 与 "None" 不兼容 (reportAssignmentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:259:15 - error: "int" 与 "int | None" 类型不支持 "<=" 运算符
    "int" 与 "None" 类型不支持 "<=" 运算符 (reportOperatorIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:312:52 - error: "int" 与 "int | None" 类型不支持 "<" 运算符
    "int" 与 "None" 类型不支持 "<" 运算符 (reportOperatorIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:340:32 - error: "CancelledError" 类型的实参无法赋值给函数 "__init__" 中 "Exception | None" 类型的形参 "last_error"
    "CancelledError" 类型与 "Exception | None" 类型不兼容
      "CancelledError" 与 "Exception" 不兼容
      "CancelledError" 与 "None" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:383:52 - error: "int" 与 "int | None" 类型不支持 "<" 运算符
    "int" 与 "None" 类型不支持 "<" 运算符 (reportOperatorIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:412:52 - error: "int" 与 "int | None" 类型不支持 "<" 运算符
    "int" 与 "None" 类型不支持 "<" 运算符 (reportOperatorIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:431:44 - error: "start_time" 可能未绑定 (reportPossiblyUnboundVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_session_manager.py:432:24 - error: "session_id" 可能未绑定 (reportPossiblyUnboundVariable)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:5:9 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:5:16 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:5:40 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:5:56 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:16:8 - error: "sys" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:20:24 - error: "asynccontextmanager" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:85:24 - error: "generator" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:85:24 - error: "generator" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:86:9 - error: "generator" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:94:15 - error: 返回类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:100:20 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:100:26 - error: "generator" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:100:26 - error: "__anext__" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:118:30 - error: "generator" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:118:30 - error: 参数类型未知
    实参对应于 "getattr" 函数中的 "o" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:123:44 - error: "object" 类型的实参无法赋值给函数 "wait_for" 中 "_FutureLike[_T@wait_for]" 类型的形参 "fut"
    "object" 类型与 "_FutureLike[_T@wait_for]" 类型不兼容
      "object" 与 Protocol 类 "Awaitable[_T@wait_for]" 不兼容
        "__await__" 不存在
      "object" 与 "Future[_T@wait_for]" 不兼容
      "object" 与 Protocol 类 "Generator[Any, None, _T@wait_for]" 不兼容
        "__next__" 不存在
        "send" 不存在
        "throw" 不存在
    ... (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:485:23 - error: "message" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:485:34 - error: "SafeAsyncGenerator" 不支持迭代
    "CoroutineType[Any, Any, SafeAsyncGenerator]" 类型上未定义 "__anext__" 方法 (reportGeneralTypeIssues)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:5:9 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:5:16 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:5:40 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:5:56 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:20:8 - error: "uuid" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:21:8 - error: "weakref" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:52:28 - error: "Dict" 未定义 (reportUndefinedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:52:38 - error: "Task" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:62:9 - error: 变量 "task_id" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:63:9 - error: "lock_waiters" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:74:13 - error: "lock_waiters" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:74:13 - error: "pop" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:82:27 - error: "Queue" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:93:19 - error: "connections" 的类型部分未知
    "connections" 为 "Queue[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:93:19 - error: "put" 的类型部分未知
    "put" 为 "(item: Unknown) -> CoroutineType[Any, Any, None]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:98:13 - error: "conn" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:98:43 - error: "connections" 的类型部分未知
    "connections" 为 "Queue[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:98:43 - error: 部分参数的类型未知
    实参对应于 "wait_for" 函数中的 "fut" 形参
    参数类型为 "CoroutineType[Any, Any, Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:99:20 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:106:19 - error: "connections" 的类型部分未知
    "connections" 为 "Queue[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:106:19 - error: "put" 的类型部分未知
    "put" 为 "(item: Unknown) -> CoroutineType[Any, Any, None]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:313:17 - error: 变量 "story_id" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:373:28 - error: 返回类型 "dict[Unknown, Any]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:373:54 - error: "k" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:373:57 - error: "v" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:375:51 - error: "v" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:517:25 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:519:28 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:549:28 - error: 返回类型 "dict[Unknown, Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:627:36 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
73 errors, 0 warnings, 0 notes
```


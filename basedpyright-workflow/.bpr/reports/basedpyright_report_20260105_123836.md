# BasedPyright 检查报告
**生成时间**: 2026-01-05 12:38:36
**检查时间**: 2026-01-05T12:38:36.483324
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 12 |
| ❌ 错误 (Error) | 53 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.61 秒 |

## 🔴 错误详情

共发现 **53** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py`: 35 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py`: 10 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py`: 8 个错误

### 按规则分组

- `reportIndexIssue`: 17 次
- `reportUnknownVariableType`: 13 次
- `reportUnknownMemberType`: 12 次
- `reportMissingImports`: 4 次
- `reportUnknownArgumentType`: 4 次
- `reportAssignmentType`: 1 次
- `reportOperatorIssue`: 1 次
- `reportUnknownParameterType`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:17

- **规则**: `reportMissingImports`
- **位置**: 第 17 行, 第 9 列
- **错误信息**: 无法解析导入 "qa_tools_integration"

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:17

- **规则**: `reportUnknownVariableType`
- **位置**: 第 17 行, 第 37 列
- **错误信息**: "QAAutomationWorkflow" 类型未知

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:17

- **规则**: `reportUnknownVariableType`
- **位置**: 第 17 行, 第 59 列
- **错误信息**: "QAStatus" 类型未知

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:448

- **规则**: `reportUnknownMemberType`
- **位置**: 第 448 行, 第 39 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:457

- **规则**: `reportUnknownMemberType`
- **位置**: 第 457 行, 第 45 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:458

- **规则**: `reportUnknownMemberType`
- **位置**: 第 458 行, 第 45 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:469

- **规则**: `reportAssignmentType`
- **位置**: 第 469 行, 第 31 列
- **错误信息**: "int" 类型不匹配声明的 "List[str]" 类型
  "int" 与 "List[str]" 不兼容

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:469

- **规则**: `reportUnknownMemberType`
- **位置**: 第 469 行, 第 41 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:470

- **规则**: `reportOperatorIssue`
- **位置**: 第 470 行, 第 23 列
- **错误信息**: "List[str]" 与 "Literal[0]" 类型不支持 ">" 运算符

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:477

- **规则**: `reportUnknownMemberType`
- **位置**: 第 477 行, 第 45 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:17

- **规则**: `reportMissingImports`
- **位置**: 第 17 行, 第 9 列
- **错误信息**: 无法解析导入 "autoBMAD.epic_automation.state_manager"

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:17

- **规则**: `reportUnknownVariableType`
- **位置**: 第 17 行, 第 55 列
- **错误信息**: "StateManager" 类型未知

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21

- **规则**: `reportMissingImports`
- **位置**: 第 21 行, 第 9 列
- **错误信息**: 无法解析导入 "fixtest_workflow.test_automation_workflow"

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21

- **规则**: `reportUnknownVariableType`
- **位置**: 第 21 行, 第 58 列
- **错误信息**: "run_pytest_execution" 类型未知

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:22

- **规则**: `reportMissingImports`
- **位置**: 第 22 行, 第 9 列
- **错误信息**: 无法解析导入 "fixtest_workflow.debugpy_integration"

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:23

- **规则**: `reportUnknownVariableType`
- **位置**: 第 23 行, 第 8 列
- **错误信息**: "start_debugpy_listener" 类型未知

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:24

- **规则**: `reportUnknownVariableType`
- **位置**: 第 24 行, 第 8 列
- **错误信息**: "attach_debugpy" 类型未知

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:25

- **规则**: `reportUnknownVariableType`
- **位置**: 第 25 行, 第 8 列
- **错误信息**: "collect_debug_info" 类型未知

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:58

- **规则**: `reportUnknownParameterType`
- **位置**: 第 58 行, 第 8 列
- **错误信息**: "state_manager" 参数的类型未知

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:81

- **规则**: `reportIndexIssue`
- **位置**: 第 81 行, 第 9 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:166

- **规则**: `reportIndexIssue`
- **位置**: 第 166 行, 第 17 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:167

- **规则**: `reportIndexIssue`
- **位置**: 第 167 行, 第 9 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:209

- **规则**: `reportIndexIssue`
- **位置**: 第 209 行, 第 17 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:210

- **规则**: `reportIndexIssue`
- **位置**: 第 210 行, 第 9 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:289

- **规则**: `reportIndexIssue`
- **位置**: 第 289 行, 第 17 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:290

- **规则**: `reportIndexIssue`
- **位置**: 第 290 行, 第 9 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:342

- **规则**: `reportIndexIssue`
- **位置**: 第 342 行, 第 9 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:388

- **规则**: `reportIndexIssue`
- **位置**: 第 388 行, 第 9 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:388

- **规则**: `reportIndexIssue`
- **位置**: 第 388 行, 第 14 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:403

- **规则**: `reportUnknownMemberType`
- **位置**: 第 403 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:414

- **规则**: `reportUnknownVariableType`
- **位置**: 第 414 行, 第 19 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:420

- **规则**: `reportIndexIssue`
- **位置**: 第 420 行, 第 40 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 33. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:420

- **规则**: `reportIndexIssue`
- **位置**: 第 420 行, 第 45 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 34. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:496

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 496 行, 第 26 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[str] | Unknown"

#### 35. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:498

- **规则**: `reportUnknownMemberType`
- **位置**: 第 498 行, 第 19 列
- **错误信息**: "startswith" 的类型部分未知
  "startswith" 为 "((prefix: str | tuple[str, ...], start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> bool) | Unknown" 类型

#### 36. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:500

- **规则**: `reportUnknownVariableType`
- **位置**: 第 500 行, 第 20 列
- **错误信息**: "file_path" 的类型部分未知
  "file_path" 为 "str | Unknown" 类型

#### 37. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:500

- **规则**: `reportUnknownMemberType`
- **位置**: 第 500 行, 第 32 列
- **错误信息**: "replace" 的类型部分未知
  "replace" 为 "((old: str, new: str, count: SupportsIndex = -1, /) -> str) | Unknown" 类型

#### 38. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:500

- **规则**: `reportUnknownMemberType`
- **位置**: 第 500 行, 第 32 列
- **错误信息**: "strip" 的类型部分未知
  "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型

#### 39. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:520

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 520 行, 第 42 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "exists" 函数中的 "path" 形参
  参数类型为 "str | Unknown"

#### 40. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:521

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 521 行, 第 33 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__new__" 函数中的 "args" 形参
  参数类型为 "str | Unknown"

#### 41. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:543

- **规则**: `reportIndexIssue`
- **位置**: 第 543 行, 第 23 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 42. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:544

- **规则**: `reportIndexIssue`
- **位置**: 第 544 行, 第 9 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 43. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:571

- **规则**: `reportIndexIssue`
- **位置**: 第 571 行, 第 17 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 44. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:572

- **规则**: `reportIndexIssue`
- **位置**: 第 572 行, 第 18 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 45. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:572

- **规则**: `reportIndexIssue`
- **位置**: 第 572 行, 第 23 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 46. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:48

- **规则**: `reportUnknownVariableType`
- **位置**: 第 48 行, 第 8 列
- **错误信息**: "workflow" 类型未知

#### 47. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:82

- **规则**: `reportUnknownVariableType`
- **位置**: 第 82 行, 第 12 列
- **错误信息**: "driver" 类型未知

#### 48. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:85

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 85 行, 第 41 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 49. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:86

- **规则**: `reportUnknownVariableType`
- **位置**: 第 86 行, 第 16 列
- **错误信息**: "story" 类型未知

#### 50. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:110

- **规则**: `reportUnknownVariableType`
- **位置**: 第 110 行, 第 12 列
- **错误信息**: "agent" 类型未知

#### 51. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:140

- **规则**: `reportUnknownMemberType`
- **位置**: 第 140 行, 第 34 列
- **错误信息**: "get" 类型未知

#### 52. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:141

- **规则**: `reportUnknownMemberType`
- **位置**: 第 141 行, 第 35 列
- **错误信息**: "get" 类型未知

#### 53. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:142

- **规则**: `reportUnknownMemberType`
- **位置**: 第 142 行, 第 41 列
- **错误信息**: "get" 类型未知

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\code_quality_agent.py`
3. `..\autoBMAD\epic_automation\dev_agent.py`
4. `..\autoBMAD\epic_automation\epic_driver.py`
5. `..\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py`
6. `..\autoBMAD\epic_automation\qa_agent.py`
7. `..\autoBMAD\epic_automation\qa_tools_integration.py`
8. `..\autoBMAD\epic_automation\sm_agent.py`
9. `..\autoBMAD\epic_automation\state_manager.py`
10. `..\autoBMAD\epic_automation\test_automation_agent.py`
11. `..\autoBMAD\epic_automation\test_changes.py`
12. `..\autoBMAD\epic_automation\test_portability.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:17:10 - error: 无法解析导入 "qa_tools_integration" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:17:38 - error: "QAAutomationWorkflow" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:17:60 - error: "QAStatus" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:448:40 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:457:46 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:458:46 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:469:32 - error: "int" 类型不匹配声明的 "List[str]" 类型
    "int" 与 "List[str]" 不兼容 (reportAssignmentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:469:42 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:470:24 - error: "List[str]" 与 "Literal[0]" 类型不支持 ">" 运算符 (reportOperatorIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:477:46 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:17:10 - error: 无法解析导入 "autoBMAD.epic_automation.state_manager" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:17:56 - error: "StateManager" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21:10 - error: 无法解析导入 "fixtest_workflow.test_automation_workflow" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21:59 - error: "run_pytest_execution" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:22:10 - error: 无法解析导入 "fixtest_workflow.debugpy_integration" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:23:9 - error: "start_debugpy_listener" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:24:9 - error: "attach_debugpy" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:25:9 - error: "collect_debug_info" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:58:9 - error: "state_manager" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:81:10 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:166:18 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:167:10 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:209:18 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:210:10 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:289:18 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:290:10 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:342:10 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:388:10 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:388:15 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:403:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:414:20 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:420:41 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:420:46 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:496:27 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[str] | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:498:20 - error: "startswith" 的类型部分未知
    "startswith" 为 "((prefix: str | tuple[str, ...], start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> bool) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:500:21 - error: "file_path" 的类型部分未知
    "file_path" 为 "str | Unknown" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:500:33 - error: "replace" 的类型部分未知
    "replace" 为 "((old: str, new: str, count: SupportsIndex = -1, /) -> str) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:500:33 - error: "strip" 的类型部分未知
    "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:520:43 - error: 部分参数的类型未知
    实参对应于 "exists" 函数中的 "path" 形参
    参数类型为 "str | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:521:34 - error: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "args" 形参
    参数类型为 "str | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:543:24 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:544:10 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:571:18 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:572:19 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:572:24 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:48:9 - error: "workflow" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:82:13 - error: "driver" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:85:42 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:86:17 - error: "story" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:110:13 - error: "agent" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:140:35 - error: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:141:36 - error: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:142:42 - error: "get" 类型未知 (reportUnknownMemberType)
53 errors, 0 warnings, 0 notes
```


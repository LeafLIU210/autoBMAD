# BasedPyright 检查报告
**生成时间**: 2026-01-05 12:54:04
**检查时间**: 2026-01-05T12:54:04.643927
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 12 |
| ❌ 错误 (Error) | 36 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.61 秒 |

## 🔴 错误详情

共发现 **36** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py`: 17 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py`: 10 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py`: 9 个错误

### 按规则分组

- `reportUnknownMemberType`: 15 次
- `reportUnknownArgumentType`: 13 次
- `reportUnknownVariableType`: 6 次
- `reportUnusedImport`: 2 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:454

- **规则**: `reportUnknownMemberType`
- **位置**: 第 454 行, 第 38 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:454

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 454 行, 第 38 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__new__" 函数中的 "x" 形参
  参数类型为 "Unknown | Literal[0]"

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:463

- **规则**: `reportUnknownMemberType`
- **位置**: 第 463 行, 第 44 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:463

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 463 行, 第 44 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__new__" 函数中的 "x" 形参
  参数类型为 "Unknown | Literal[0]"

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:464

- **规则**: `reportUnknownMemberType`
- **位置**: 第 464 行, 第 44 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:464

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 464 行, 第 44 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__new__" 函数中的 "x" 形参
  参数类型为 "Unknown | Literal[0]"

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:475

- **规则**: `reportUnknownMemberType`
- **位置**: 第 475 行, 第 43 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:475

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 475 行, 第 43 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__new__" 函数中的 "x" 形参
  参数类型为 "Unknown | Literal[0]"

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:483

- **规则**: `reportUnknownMemberType`
- **位置**: 第 483 行, 第 53 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:483

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 483 行, 第 53 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__new__" 函数中的 "x" 形参
  参数类型为 "Unknown | Literal[0]"

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:495

- **规则**: `reportUnknownVariableType`
- **位置**: 第 495 行, 第 12 列
- **错误信息**: "lines" 的类型部分未知
  "lines" 为 "list[str] | Unknown" 类型

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:495

- **规则**: `reportUnknownMemberType`
- **位置**: 第 495 行, 第 31 列
- **错误信息**: "split" 的类型部分未知
  "split" 为 "Unknown | ((sep: str | None = None, maxsplit: SupportsIndex = -1) -> list[str])" 类型

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:497

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 497 行, 第 26 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[str] | Unknown"

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:498

- **规则**: `reportUnknownVariableType`
- **位置**: 第 498 行, 第 16 列
- **错误信息**: "line" 的类型部分未知
  "line" 为 "str | Unknown" 类型

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:498

- **规则**: `reportUnknownMemberType`
- **位置**: 第 498 行, 第 28 列
- **错误信息**: "strip" 的类型部分未知
  "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:499

- **规则**: `reportUnknownMemberType`
- **位置**: 第 499 行, 第 19 列
- **错误信息**: "startswith" 的类型部分未知
  "startswith" 为 "((prefix: str | tuple[str, ...], start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> bool) | Unknown" 类型

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:501

- **规则**: `reportUnknownVariableType`
- **位置**: 第 501 行, 第 20 列
- **错误信息**: "file_path" 的类型部分未知
  "file_path" 为 "str | Unknown" 类型

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:501

- **规则**: `reportUnknownMemberType`
- **位置**: 第 501 行, 第 37 列
- **错误信息**: "replace" 的类型部分未知
  "replace" 为 "((old: str, new: str, count: SupportsIndex = -1, /) -> str) | Unknown" 类型

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:501

- **规则**: `reportUnknownMemberType`
- **位置**: 第 501 行, 第 37 列
- **错误信息**: "strip" 的类型部分未知
  "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:505

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 505 行, 第 34 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[str] | Unknown"

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:508

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 508 行, 第 32 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[str] | Unknown"

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:515

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 515 行, 第 34 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[str] | Unknown"

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:515

- **规则**: `reportUnknownMemberType`
- **位置**: 第 515 行, 第 49 列
- **错误信息**: "strip" 的类型部分未知
  "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:515

- **规则**: `reportUnknownMemberType`
- **位置**: 第 515 行, 第 49 列
- **错误信息**: "startswith" 的类型部分未知
  "startswith" 为 "((prefix: str | tuple[str, ...], start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> bool) | Unknown" 类型

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:516

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 516 行, 第 48 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "append" 函数中的 "object" 形参
  参数类型为 "str | Unknown"

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:521

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 521 行, 第 42 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "exists" 函数中的 "path" 形参
  参数类型为 "str | Unknown"

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:522

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 522 行, 第 33 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__new__" 函数中的 "args" 形参
  参数类型为 "str | Unknown"

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:6

- **规则**: `reportUnusedImport`
- **位置**: 第 6 行, 第 36 列
- **错误信息**: "Optional" 导入项未使用

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:6

- **规则**: `reportUnusedImport`
- **位置**: 第 6 行, 第 46 列
- **错误信息**: "Union" 导入项未使用

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:49

- **规则**: `reportUnknownVariableType`
- **位置**: 第 49 行, 第 8 列
- **错误信息**: "workflow" 类型未知

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:83

- **规则**: `reportUnknownVariableType`
- **位置**: 第 83 行, 第 12 列
- **错误信息**: "driver" 类型未知

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:86

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 86 行, 第 41 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "Unknown | List[Dict[str, Any]]"

#### 33. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:111

- **规则**: `reportUnknownVariableType`
- **位置**: 第 111 行, 第 12 列
- **错误信息**: "agent" 类型未知

#### 34. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:141

- **规则**: `reportUnknownMemberType`
- **位置**: 第 141 行, 第 34 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型

#### 35. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:142

- **规则**: `reportUnknownMemberType`
- **位置**: 第 142 行, 第 35 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型

#### 36. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:143

- **规则**: `reportUnknownMemberType`
- **位置**: 第 143 行, 第 41 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型

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
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:454:39 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:454:39 - error: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "x" 形参
    参数类型为 "Unknown | Literal[0]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:463:45 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:463:45 - error: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "x" 形参
    参数类型为 "Unknown | Literal[0]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:464:45 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:464:45 - error: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "x" 形参
    参数类型为 "Unknown | Literal[0]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:475:44 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:475:44 - error: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "x" 形参
    参数类型为 "Unknown | Literal[0]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:483:54 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:483:54 - error: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "x" 形参
    参数类型为 "Unknown | Literal[0]" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:495:13 - error: "lines" 的类型部分未知
    "lines" 为 "list[str] | Unknown" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:495:32 - error: "split" 的类型部分未知
    "split" 为 "Unknown | ((sep: str | None = None, maxsplit: SupportsIndex = -1) -> list[str])" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:497:27 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[str] | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:498:17 - error: "line" 的类型部分未知
    "line" 为 "str | Unknown" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:498:29 - error: "strip" 的类型部分未知
    "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:499:20 - error: "startswith" 的类型部分未知
    "startswith" 为 "((prefix: str | tuple[str, ...], start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> bool) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:501:21 - error: "file_path" 的类型部分未知
    "file_path" 为 "str | Unknown" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:501:38 - error: "replace" 的类型部分未知
    "replace" 为 "((old: str, new: str, count: SupportsIndex = -1, /) -> str) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:501:38 - error: "strip" 的类型部分未知
    "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:505:35 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[str] | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:508:33 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[str] | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:515:35 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[str] | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:515:50 - error: "strip" 的类型部分未知
    "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:515:50 - error: "startswith" 的类型部分未知
    "startswith" 为 "((prefix: str | tuple[str, ...], start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> bool) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:516:49 - error: 部分参数的类型未知
    实参对应于 "append" 函数中的 "object" 形参
    参数类型为 "str | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:521:43 - error: 部分参数的类型未知
    实参对应于 "exists" 函数中的 "path" 形参
    参数类型为 "str | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:522:34 - error: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "args" 形参
    参数类型为 "str | Unknown" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:6:37 - error: "Optional" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:6:47 - error: "Union" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:49:9 - error: "workflow" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:83:13 - error: "driver" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:86:42 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "Unknown | List[Dict[str, Any]]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:111:13 - error: "agent" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:141:35 - error: "get" 的类型部分未知
    "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:142:36 - error: "get" 的类型部分未知
    "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:143:42 - error: "get" 的类型部分未知
    "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型 (reportUnknownMemberType)
36 errors, 0 warnings, 0 notes
```


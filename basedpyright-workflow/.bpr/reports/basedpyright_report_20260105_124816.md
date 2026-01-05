# BasedPyright 检查报告
**生成时间**: 2026-01-05 12:48:16
**检查时间**: 2026-01-05T12:48:15.601433
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 12 |
| ❌ 错误 (Error) | 38 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.61 秒 |

## 🔴 错误详情

共发现 **38** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py`: 16 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py`: 15 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py`: 7 个错误

### 按规则分组

- `reportUnknownVariableType`: 17 次
- `reportUnknownMemberType`: 12 次
- `reportMissingImports`: 4 次
- `reportUnknownArgumentType`: 4 次
- `reportUnusedImport`: 1 次

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

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:385

- **规则**: `reportUnknownMemberType`
- **位置**: 第 385 行, 第 59 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:386

- **规则**: `reportUnknownVariableType`
- **位置**: 第 386 行, 第 19 列
- **错误信息**: 返回类型 "Unknown | Dict[str, Any]" 部分未知

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:453

- **规则**: `reportUnknownVariableType`
- **位置**: 第 453 行, 第 20 列
- **错误信息**: "errors" 类型未知

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:453

- **规则**: `reportUnknownMemberType`
- **位置**: 第 453 行, 第 29 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:462

- **规则**: `reportUnknownVariableType`
- **位置**: 第 462 行, 第 20 列
- **错误信息**: "tests_failed" 类型未知

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:462

- **规则**: `reportUnknownMemberType`
- **位置**: 第 462 行, 第 35 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:463

- **规则**: `reportUnknownVariableType`
- **位置**: 第 463 行, 第 20 列
- **错误信息**: "tests_errors" 类型未知

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:463

- **规则**: `reportUnknownMemberType`
- **位置**: 第 463 行, 第 35 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:474

- **规则**: `reportUnknownVariableType`
- **位置**: 第 474 行, 第 20 列
- **错误信息**: "bp_warnings" 类型未知

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:474

- **规则**: `reportUnknownMemberType`
- **位置**: 第 474 行, 第 34 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:482

- **规则**: `reportUnknownVariableType`
- **位置**: 第 482 行, 第 20 列
- **错误信息**: "tests_failed" 类型未知

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:482

- **规则**: `reportUnknownMemberType`
- **位置**: 第 482 行, 第 35 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:17

- **规则**: `reportMissingImports`
- **位置**: 第 17 行, 第 9 列
- **错误信息**: 无法解析导入 "autoBMAD.epic_automation.state_manager"

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:17

- **规则**: `reportUnknownVariableType`
- **位置**: 第 17 行, 第 55 列
- **错误信息**: "StateManager" 类型未知

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:17

- **规则**: `reportUnusedImport`
- **位置**: 第 17 行, 第 55 列
- **错误信息**: "StateManager" 导入项未使用

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21

- **规则**: `reportMissingImports`
- **位置**: 第 21 行, 第 9 列
- **错误信息**: 无法解析导入 "fixtest_workflow.test_automation_workflow"

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21

- **规则**: `reportUnknownVariableType`
- **位置**: 第 21 行, 第 58 列
- **错误信息**: "run_pytest_execution" 类型未知

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:22

- **规则**: `reportMissingImports`
- **位置**: 第 22 行, 第 9 列
- **错误信息**: 无法解析导入 "fixtest_workflow.debugpy_integration"

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:23

- **规则**: `reportUnknownVariableType`
- **位置**: 第 23 行, 第 8 列
- **错误信息**: "start_debugpy_listener" 类型未知

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:24

- **规则**: `reportUnknownVariableType`
- **位置**: 第 24 行, 第 8 列
- **错误信息**: "attach_debugpy" 类型未知

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:25

- **规则**: `reportUnknownVariableType`
- **位置**: 第 25 行, 第 8 列
- **错误信息**: "collect_debug_info" 类型未知

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:496

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 496 行, 第 26 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[str] | Unknown"

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:498

- **规则**: `reportUnknownMemberType`
- **位置**: 第 498 行, 第 19 列
- **错误信息**: "startswith" 的类型部分未知
  "startswith" 为 "((prefix: str | tuple[str, ...], start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> bool) | Unknown" 类型

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:500

- **规则**: `reportUnknownVariableType`
- **位置**: 第 500 行, 第 20 列
- **错误信息**: "file_path" 的类型部分未知
  "file_path" 为 "str | Unknown" 类型

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:500

- **规则**: `reportUnknownMemberType`
- **位置**: 第 500 行, 第 32 列
- **错误信息**: "replace" 的类型部分未知
  "replace" 为 "((old: str, new: str, count: SupportsIndex = -1, /) -> str) | Unknown" 类型

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:500

- **规则**: `reportUnknownMemberType`
- **位置**: 第 500 行, 第 32 列
- **错误信息**: "strip" 的类型部分未知
  "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:520

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 520 行, 第 42 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "exists" 函数中的 "path" 形参
  参数类型为 "str | Unknown"

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:521

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 521 行, 第 33 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__new__" 函数中的 "args" 形参
  参数类型为 "str | Unknown"

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:49

- **规则**: `reportUnknownVariableType`
- **位置**: 第 49 行, 第 8 列
- **错误信息**: "workflow" 类型未知

#### 33. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:83

- **规则**: `reportUnknownVariableType`
- **位置**: 第 83 行, 第 12 列
- **错误信息**: "driver" 类型未知

#### 34. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:86

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 86 行, 第 41 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "Unknown | Any"

#### 35. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:111

- **规则**: `reportUnknownVariableType`
- **位置**: 第 111 行, 第 12 列
- **错误信息**: "agent" 类型未知

#### 36. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:141

- **规则**: `reportUnknownMemberType`
- **位置**: 第 141 行, 第 34 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Unknown | Any" 类型

#### 37. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:142

- **规则**: `reportUnknownMemberType`
- **位置**: 第 142 行, 第 35 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Unknown | Any" 类型

#### 38. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:143

- **规则**: `reportUnknownMemberType`
- **位置**: 第 143 行, 第 41 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Unknown | Any" 类型

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
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:385:60 - error: "get" 的类型部分未知
    "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:386:20 - error: 返回类型 "Unknown | Dict[str, Any]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:453:21 - error: "errors" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:453:30 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:462:21 - error: "tests_failed" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:462:36 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:463:21 - error: "tests_errors" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:463:36 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:474:21 - error: "bp_warnings" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:474:35 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:482:21 - error: "tests_failed" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:482:36 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:17:10 - error: 无法解析导入 "autoBMAD.epic_automation.state_manager" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:17:56 - error: "StateManager" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:17:56 - error: "StateManager" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21:10 - error: 无法解析导入 "fixtest_workflow.test_automation_workflow" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21:59 - error: "run_pytest_execution" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:22:10 - error: 无法解析导入 "fixtest_workflow.debugpy_integration" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:23:9 - error: "start_debugpy_listener" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:24:9 - error: "attach_debugpy" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:25:9 - error: "collect_debug_info" 类型未知 (reportUnknownVariableType)
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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:49:9 - error: "workflow" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:83:13 - error: "driver" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:86:42 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "Unknown | Any" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:111:13 - error: "agent" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:141:35 - error: "get" 的类型部分未知
    "get" 为 "Unknown | Any" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:142:36 - error: "get" 的类型部分未知
    "get" 为 "Unknown | Any" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:143:42 - error: "get" 的类型部分未知
    "get" 为 "Unknown | Any" 类型 (reportUnknownMemberType)
38 errors, 0 warnings, 0 notes
```


# BasedPyright 检查报告
**生成时间**: 2026-01-05 15:25:00
**检查时间**: 2026-01-05T15:25:00.097310
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 10 |
| ❌ 错误 (Error) | 31 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.57 秒 |

## 🔴 错误详情

共发现 **31** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 16 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py`: 15 个错误

### 按规则分组

- `reportUnknownVariableType`: 13 次
- `reportUnknownMemberType`: 7 次
- `reportUnknownArgumentType`: 5 次
- `reportUnusedVariable`: 2 次
- `reportUnusedImport`: 1 次
- `reportMissingImports`: 1 次
- `reportUnknownParameterType`: 1 次
- `reportArgumentType`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:833

- **规则**: `reportUnknownVariableType`
- **位置**: 第 833 行, 第 12 列
- **错误信息**: "quality_agent" 类型未知

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:839

- **规则**: `reportUnknownVariableType`
- **位置**: 第 839 行, 第 12 列
- **错误信息**: "quality_results" 的类型部分未知
  "quality_results" 为 "Unknown | Any" 类型

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:839

- **规则**: `reportUnknownMemberType`
- **位置**: 第 839 行, 第 52 列
- **错误信息**: "run_quality_gates" 的类型部分未知
  "run_quality_gates" 为 "Unknown | Any" 类型

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:845

- **规则**: `reportUnknownVariableType`
- **位置**: 第 845 行, 第 12 列
- **错误信息**: "status" 的类型部分未知
  "status" 为 "Any | Unknown" 类型

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:845

- **规则**: `reportUnknownMemberType`
- **位置**: 第 845 行, 第 26 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:846

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 846 行, 第 57 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "_update_progress" 函数中的 "status" 形参
  参数类型为 "str | Unknown"

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:846

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 846 行, 第 65 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "_update_progress" 函数中的 "details" 形参
  参数类型为 "Unknown | Dict[str, Any]"

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:855

- **规则**: `reportUnknownVariableType`
- **位置**: 第 855 行, 第 19 列
- **错误信息**: 返回类型 "Unknown | Dict[str, Any]" 部分未知

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:880

- **规则**: `reportUnknownVariableType`
- **位置**: 第 880 行, 第 12 列
- **错误信息**: "test_agent" 类型未知

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:886

- **规则**: `reportUnknownVariableType`
- **位置**: 第 886 行, 第 12 列
- **错误信息**: "test_results" 的类型部分未知
  "test_results" 为 "Unknown | Any" 类型

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:886

- **规则**: `reportUnknownMemberType`
- **位置**: 第 886 行, 第 49 列
- **错误信息**: "run_test_automation" 的类型部分未知
  "run_test_automation" 为 "Unknown | Any" 类型

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:892

- **规则**: `reportUnknownVariableType`
- **位置**: 第 892 行, 第 12 列
- **错误信息**: "status" 的类型部分未知
  "status" 为 "Any | Unknown" 类型

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:892

- **规则**: `reportUnknownMemberType`
- **位置**: 第 892 行, 第 26 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:893

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 893 行, 第 59 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "_update_progress" 函数中的 "status" 形参
  参数类型为 "str | Unknown"

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:893

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 893 行, 第 67 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "_update_progress" 函数中的 "details" 形参
  参数类型为 "Unknown | Dict[str, Any]"

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:902

- **规则**: `reportUnknownVariableType`
- **位置**: 第 902 行, 第 19 列
- **错误信息**: 返回类型 "Unknown | Dict[str, Any]" 部分未知

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:10

- **规则**: `reportUnusedImport`
- **位置**: 第 10 行, 第 36 列
- **错误信息**: "Optional" 导入项未使用

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:13

- **规则**: `reportMissingImports`
- **位置**: 第 13 行, 第 5 列
- **错误信息**: 无法解析导入 "autoBMAD.epic_automation.state_manager"

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:13

- **规则**: `reportUnknownVariableType`
- **位置**: 第 13 行, 第 51 列
- **错误信息**: "StateManager" 类型未知

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:20

- **规则**: `reportUnknownParameterType`
- **位置**: 第 20 行, 第 23 列
- **错误信息**: "state_manager" 参数的类型未知

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21

- **规则**: `reportUnknownMemberType`
- **位置**: 第 21 行, 第 8 列
- **错误信息**: "state_manager" 类型未知

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:41

- **规则**: `reportUnknownVariableType`
- **位置**: 第 41 行, 第 8 列
- **错误信息**: "results" 的类型部分未知
  "results" 为 "dict[str, str | dict[str, int | float] | list[Unknown]]" 类型

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:63

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 63 行, 第 52 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "generate_test_report" 函数中的 "results" 形参
  参数类型为 "dict[str, str | dict[str, int | float] | list[Unknown]]"

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:63

- **规则**: `reportUnknownMemberType`
- **位置**: 第 63 行, 第 61 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: str, default: None = None, /) -> (str | dict[str, int | float] | list[Unknown] | None), (key: str, default: str | dict[str, int | float] | list[Unknown], /) -> (str | dict[str, int | float] | list[Unknown]), (key: str, default: _T@get, /) -> (str | dict[str, int | float] | _T@get | list[Unknown])]" 类型

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:63

- **规则**: `reportArgumentType`
- **位置**: 第 63 行, 第 61 列
- **错误信息**: "str | dict[str, int | float] | list[Unknown]" 类型的实参无法赋值给函数 "generate_test_report" 中 "List[Dict[str, Any]]" 类型的形参 "failures"
  "str | dict[str, int | float] | list[Unknown]" 类型与 "List[Dict[str, Any]]" 类型不兼容
    "str" 与 "List[Dict[str, Any]]" 不兼容

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:66

- **规则**: `reportUnknownVariableType`
- **位置**: 第 66 行, 第 19 列
- **错误信息**: 返回类型 "dict[str, str | dict[str, int | float] | list[Unknown]]" 部分未知

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:72

- **规则**: `reportUnknownVariableType`
- **位置**: 第 72 行, 第 19 列
- **错误信息**: 返回类型 "dict[str, str | dict[str, int | float] | list[Unknown]]" 部分未知

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:78

- **规则**: `reportUnusedVariable`
- **位置**: 第 78 行, 第 12 列
- **错误信息**: 变量 "stdout" 未使用

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:78

- **规则**: `reportUnusedVariable`
- **位置**: 第 78 行, 第 20 列
- **错误信息**: 变量 "stderr" 未使用

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:114

- **规则**: `reportUnknownMemberType`
- **位置**: 第 114 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:115

- **规则**: `reportUnknownVariableType`
- **位置**: 第 115 行, 第 19 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

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

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:833:13 - error: "quality_agent" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:839:13 - error: "quality_results" 的类型部分未知
    "quality_results" 为 "Unknown | Any" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:839:53 - error: "run_quality_gates" 的类型部分未知
    "run_quality_gates" 为 "Unknown | Any" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:845:13 - error: "status" 的类型部分未知
    "status" 为 "Any | Unknown" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:845:27 - error: "get" 的类型部分未知
    "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:846:58 - error: 部分参数的类型未知
    实参对应于 "_update_progress" 函数中的 "status" 形参
    参数类型为 "str | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:846:66 - error: 部分参数的类型未知
    实参对应于 "_update_progress" 函数中的 "details" 形参
    参数类型为 "Unknown | Dict[str, Any]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:855:20 - error: 返回类型 "Unknown | Dict[str, Any]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:880:13 - error: "test_agent" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:886:13 - error: "test_results" 的类型部分未知
    "test_results" 为 "Unknown | Any" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:886:50 - error: "run_test_automation" 的类型部分未知
    "run_test_automation" 为 "Unknown | Any" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:892:13 - error: "status" 的类型部分未知
    "status" 为 "Any | Unknown" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:892:27 - error: "get" 的类型部分未知
    "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:893:60 - error: 部分参数的类型未知
    实参对应于 "_update_progress" 函数中的 "status" 形参
    参数类型为 "str | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:893:68 - error: 部分参数的类型未知
    实参对应于 "_update_progress" 函数中的 "details" 形参
    参数类型为 "Unknown | Dict[str, Any]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:902:20 - error: 返回类型 "Unknown | Dict[str, Any]" 部分未知 (reportUnknownVariableType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:10:37 - error: "Optional" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:13:6 - error: 无法解析导入 "autoBMAD.epic_automation.state_manager" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:13:52 - error: "StateManager" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:20:24 - error: "state_manager" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21:9 - error: "state_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:41:9 - error: "results" 的类型部分未知
    "results" 为 "dict[str, str | dict[str, int | float] | list[Unknown]]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:63:53 - error: 部分参数的类型未知
    实参对应于 "generate_test_report" 函数中的 "results" 形参
    参数类型为 "dict[str, str | dict[str, int | float] | list[Unknown]]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:63:62 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: str, default: None = None, /) -> (str | dict[str, int | float] | list[Unknown] | None), (key: str, default: str | dict[str, int | float] | list[Unknown], /) -> (str | dict[str, int | float] | list[Unknown]), (key: str, default: _T@get, /) -> (str | dict[str, int | float] | _T@get | list[Unknown])]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:63:62 - error: "str | dict[str, int | float] | list[Unknown]" 类型的实参无法赋值给函数 "generate_test_report" 中 "List[Dict[str, Any]]" 类型的形参 "failures"
    "str | dict[str, int | float] | list[Unknown]" 类型与 "List[Dict[str, Any]]" 类型不兼容
      "str" 与 "List[Dict[str, Any]]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:66:20 - error: 返回类型 "dict[str, str | dict[str, int | float] | list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:72:20 - error: 返回类型 "dict[str, str | dict[str, int | float] | list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:78:13 - error: 变量 "stdout" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:78:21 - error: 变量 "stderr" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:114:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:115:20 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
31 errors, 0 warnings, 0 notes
```


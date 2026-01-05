# BasedPyright 检查报告
**生成时间**: 2026-01-05 13:01:41
**检查时间**: 2026-01-05T13:01:41.252434
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 12 |
| ❌ 错误 (Error) | 8 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.60 秒 |

## 🔴 错误详情

共发现 **8** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py`: 7 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py`: 1 个错误

### 按规则分组

- `reportUnknownVariableType`: 3 次
- `reportUnknownMemberType`: 3 次
- `reportUnknownArgumentType`: 2 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:495

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 495 行, 第 41 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__new__" 函数中的 "object" 形参
  参数类型为 "Unknown | str"

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:49

- **规则**: `reportUnknownVariableType`
- **位置**: 第 49 行, 第 8 列
- **错误信息**: "workflow" 类型未知

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:83

- **规则**: `reportUnknownVariableType`
- **位置**: 第 83 行, 第 12 列
- **错误信息**: "driver" 类型未知

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:86

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 86 行, 第 41 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "Unknown | List[Dict[str, Any]]"

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:111

- **规则**: `reportUnknownVariableType`
- **位置**: 第 111 行, 第 12 列
- **错误信息**: "agent" 类型未知

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:141

- **规则**: `reportUnknownMemberType`
- **位置**: 第 141 行, 第 30 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:142

- **规则**: `reportUnknownMemberType`
- **位置**: 第 142 行, 第 32 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:143

- **规则**: `reportUnknownMemberType`
- **位置**: 第 143 行, 第 39 列
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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:495:42 - error: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "object" 形参
    参数类型为 "Unknown | str" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:49:9 - error: "workflow" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:83:13 - error: "driver" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:86:42 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "Unknown | List[Dict[str, Any]]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:111:13 - error: "agent" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:141:31 - error: "get" 的类型部分未知
    "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:142:33 - error: "get" 的类型部分未知
    "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:143:40 - error: "get" 的类型部分未知
    "get" 为 "Unknown | Overload[(key: str, default: None = None, /) -> (Any | None), (key: str, default: Any, /) -> Any, (key: str, default: _T@get, /) -> (Any | _T@get)]" 类型 (reportUnknownMemberType)
8 errors, 0 warnings, 0 notes
```


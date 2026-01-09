# BasedPyright 检查报告
**生成时间**: 2026-01-06 21:12:05
**检查时间**: 2026-01-06T21:12:05.212895
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 16 |
| ❌ 错误 (Error) | 25 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.11 秒 |

## 🔴 错误详情

共发现 **25** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 21 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py`: 1 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py`: 1 个错误

### 按规则分组

- `reportUnknownMemberType`: 7 次
- `reportPossiblyUnboundVariable`: 4 次
- `reportUnknownArgumentType`: 4 次
- `reportUnknownLambdaType`: 4 次
- `reportOptionalCall`: 2 次
- `reportUnknownVariableType`: 2 次
- `reportArgumentType`: 1 次
- `reportUnnecessaryComparison`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:504

- **规则**: `reportOptionalCall`
- **位置**: 第 504 行, 第 22 列
- **错误信息**: `None` 不支持调用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:717

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 717 行, 第 63 列
- **错误信息**: "story_path" 可能未绑定

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:743

- **规则**: `reportUnknownMemberType`
- **位置**: 第 743 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:745

- **规则**: `reportUnknownMemberType`
- **位置**: 第 745 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:749

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 749 行, 第 63 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:749

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 749 行, 第 94 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:792

- **规则**: `reportUnknownVariableType`
- **位置**: 第 792 行, 第 12 列
- **错误信息**: "essential_elements" 的类型部分未知
  "essential_elements" 为 "list[tuple[str, (c: Unknown) -> (Unknown | Literal[True])] | tuple[str, (c: Unknown) -> bool]]" 类型

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:793

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 793 行, 第 43 列
- **错误信息**: "c" 参数的类型未知

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:793

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 793 行, 第 46 列
- **错误信息**: 该 `lambda` 的返回类型 "Unknown | Literal[True]" 部分未知

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:793

- **规则**: `reportUnknownMemberType`
- **位置**: 第 793 行, 第 58 列
- **错误信息**: "strip" 类型未知

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:793

- **规则**: `reportUnknownMemberType`
- **位置**: 第 793 行, 第 58 列
- **错误信息**: "startswith" 类型未知

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:794

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 794 行, 第 34 列
- **错误信息**: "c" 参数的类型未知

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:794

- **规则**: `reportUnknownMemberType`
- **位置**: 第 794 行, 第 49 列
- **错误信息**: "lower" 类型未知

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:795

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 795 行, 第 41 列
- **错误信息**: "c" 参数的类型未知

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:795

- **规则**: `reportUnknownMemberType`
- **位置**: 第 795 行, 第 48 列
- **错误信息**: "split" 类型未知

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:795

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 795 行, 第 48 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:799

- **规则**: `reportUnknownVariableType`
- **位置**: 第 799 行, 第 30 列
- **错误信息**: "check_func" 的类型部分未知
  "check_func" 为 "((c: Unknown) -> (Unknown | Literal[True])) | ((c: Unknown) -> bool)" 类型

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:801

- **规则**: `reportUnknownMemberType`
- **位置**: 第 801 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:807

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 807 行, 第 23 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:827

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 827 行, 第 66 列
- **错误信息**: "story_path" 可能未绑定

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:856

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 856 行, 第 61 列
- **错误信息**: "story_path" 可能未绑定

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:882

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 882 行, 第 71 列
- **错误信息**: "story_path" 可能未绑定

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:526

- **规则**: `reportArgumentType`
- **位置**: 第 526 行, 第 51 列
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

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:518

- **规则**: `reportUnnecessaryComparison`
- **位置**: 第 518 行, 第 11 列
- **错误信息**: 条件的计算结果始终为 `False`，因为类型 "SDKSessionManager" 和 "None" 之间不存在交集

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:524

- **规则**: `reportOptionalCall`
- **位置**: 第 524 行, 第 22 列
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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:504:23 - error: `None` 不支持调用 (reportOptionalCall)
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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:526:52 - error: "object" 类型的实参无法赋值给函数 "wait_for" 中 "_FutureLike[_T@wait_for]" 类型的形参 "fut"
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
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:518:12 - error: 条件的计算结果始终为 `False`，因为类型 "SDKSessionManager" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:524:23 - error: `None` 不支持调用 (reportOptionalCall)
25 errors, 0 warnings, 0 notes
```


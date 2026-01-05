# BasedPyright 检查报告
**生成时间**: 2026-01-05 18:17:02
**检查时间**: 2026-01-05T18:17:01.756153
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 10 |
| ❌ 错误 (Error) | 32 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.62 秒 |

## 🔴 错误详情

共发现 **32** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py`: 20 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py`: 8 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 1 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py`: 1 个错误

### 按规则分组

- `reportAttributeAccessIssue`: 12 次
- `reportUnknownMemberType`: 9 次
- `reportOptionalCall`: 2 次
- `reportArgumentType`: 2 次
- `reportOptionalSubscript`: 1 次
- `reportUnusedImport`: 1 次
- `reportPossiblyUnboundVariable`: 1 次
- `reportUnusedVariable`: 1 次
- `reportUnknownArgumentType`: 1 次
- `reportUnknownVariableType`: 1 次
- `reportUnknownParameterType`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:329

- **规则**: `reportOptionalCall`
- **位置**: 第 329 行, 第 22 列
- **错误信息**: `None` 不支持调用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:342

- **规则**: `reportOptionalCall`
- **位置**: 第 342 行, 第 41 列
- **错误信息**: `None` 不支持调用

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:344

- **规则**: `reportArgumentType`
- **位置**: 第 344 行, 第 47 列
- **错误信息**: "type[ResultMessage] | None" 类型的实参无法赋值给函数 "isinstance" 中 "_ClassInfo" 类型的形参 "class_or_tuple"
  "type[ResultMessage] | None" 类型与 "_ClassInfo" 类型不兼容
    "None" 类型与 "_ClassInfo" 类型不兼容
      "None" 与 "type" 不兼容
      "None" 与 "tuple[_ClassInfo, ...]" 不兼容

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:344

- **规则**: `reportArgumentType`
- **位置**: 第 344 行, 第 47 列
- **错误信息**: `isinstance` 的第二个参数必须是单个类或由多个类构成的元组
  `None` 不能参与 `isinstance()` 或 `issubclass()`

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:345

- **规则**: `reportUnknownMemberType`
- **位置**: 第 345 行, 第 31 列
- **错误信息**: "is_error" 的类型部分未知
  "is_error" 为 "Unknown | bool" 类型

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:345

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 345 行, 第 39 列
- **错误信息**: 无法访问 "UserMessage" 类的 "is_error" 属性
  属性 "is_error" 未知

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:345

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 345 行, 第 39 列
- **错误信息**: 无法访问 "AssistantMessage" 类的 "is_error" 属性
  属性 "is_error" 未知

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:345

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 345 行, 第 39 列
- **错误信息**: 无法访问 "SystemMessage" 类的 "is_error" 属性
  属性 "is_error" 未知

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:345

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 345 行, 第 39 列
- **错误信息**: 无法访问 "StreamEvent" 类的 "is_error" 属性
  属性 "is_error" 未知

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:346

- **规则**: `reportUnknownMemberType`
- **位置**: 第 346 行, 第 69 列
- **错误信息**: "result" 的类型部分未知
  "result" 为 "Unknown | str | None" 类型

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:346

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 346 行, 第 77 列
- **错误信息**: 无法访问 "UserMessage" 类的 "result" 属性
  属性 "result" 未知

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:346

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 346 行, 第 77 列
- **错误信息**: 无法访问 "AssistantMessage" 类的 "result" 属性
  属性 "result" 未知

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:346

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 346 行, 第 77 列
- **错误信息**: 无法访问 "SystemMessage" 类的 "result" 属性
  属性 "result" 未知

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:346

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 346 行, 第 77 列
- **错误信息**: 无法访问 "StreamEvent" 类的 "result" 属性
  属性 "result" 未知

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:352

- **规则**: `reportUnknownMemberType`
- **位置**: 第 352 行, 第 68 列
- **错误信息**: "result" 的类型部分未知
  "result" 为 "Unknown | str | None" 类型

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:352

- **规则**: `reportOptionalSubscript`
- **位置**: 第 352 行, 第 68 列
- **错误信息**: `None` 不支持下标访问

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:352

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 352 行, 第 76 列
- **错误信息**: 无法访问 "UserMessage" 类的 "result" 属性
  属性 "result" 未知

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:352

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 352 行, 第 76 列
- **错误信息**: 无法访问 "AssistantMessage" 类的 "result" 属性
  属性 "result" 未知

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:352

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 352 行, 第 76 列
- **错误信息**: 无法访问 "SystemMessage" 类的 "result" 属性
  属性 "result" 未知

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:352

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 352 行, 第 76 列
- **错误信息**: 无法访问 "StreamEvent" 类的 "result" 属性
  属性 "result" 未知

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:13

- **规则**: `reportUnusedImport`
- **位置**: 第 13 行, 第 36 列
- **错误信息**: "Optional" 导入项未使用

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:617

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 617 行, 第 15 列
- **错误信息**: "subprocess" 可能未绑定

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:316

- **规则**: `reportUnusedVariable`
- **位置**: 第 316 行, 第 23 列
- **错误信息**: 变量 "title" 未使用

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:514

- **规则**: `reportUnknownMemberType`
- **位置**: 第 514 行, 第 16 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:527

- **规则**: `reportUnknownMemberType`
- **位置**: 第 527 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:544

- **规则**: `reportUnknownMemberType`
- **位置**: 第 544 行, 第 24 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:548

- **规则**: `reportUnknownMemberType`
- **位置**: 第 548 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:555

- **规则**: `reportUnknownMemberType`
- **位置**: 第 555 行, 第 16 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:558

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 558 行, 第 50 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:559

- **规则**: `reportUnknownVariableType`
- **位置**: 第 559 行, 第 19 列
- **错误信息**: 返回类型 "tuple[Literal[False], list[Unknown]]" 部分未知

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:20

- **规则**: `reportUnknownParameterType`
- **位置**: 第 20 行, 第 23 列
- **错误信息**: "state_manager" 参数的类型未知

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21

- **规则**: `reportUnknownMemberType`
- **位置**: 第 21 行, 第 8 列
- **错误信息**: "state_manager" 类型未知

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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:329:23 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:342:42 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:344:48 - error: "type[ResultMessage] | None" 类型的实参无法赋值给函数 "isinstance" 中 "_ClassInfo" 类型的形参 "class_or_tuple"
    "type[ResultMessage] | None" 类型与 "_ClassInfo" 类型不兼容
      "None" 类型与 "_ClassInfo" 类型不兼容
        "None" 与 "type" 不兼容
        "None" 与 "tuple[_ClassInfo, ...]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:344:48 - error: `isinstance` 的第二个参数必须是单个类或由多个类构成的元组
    `None` 不能参与 `isinstance()` 或 `issubclass()` (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:345:32 - error: "is_error" 的类型部分未知
    "is_error" 为 "Unknown | bool" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:345:40 - error: 无法访问 "UserMessage" 类的 "is_error" 属性
    属性 "is_error" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:345:40 - error: 无法访问 "AssistantMessage" 类的 "is_error" 属性
    属性 "is_error" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:345:40 - error: 无法访问 "SystemMessage" 类的 "is_error" 属性
    属性 "is_error" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:345:40 - error: 无法访问 "StreamEvent" 类的 "is_error" 属性
    属性 "is_error" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:346:70 - error: "result" 的类型部分未知
    "result" 为 "Unknown | str | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:346:78 - error: 无法访问 "UserMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:346:78 - error: 无法访问 "AssistantMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:346:78 - error: 无法访问 "SystemMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:346:78 - error: 无法访问 "StreamEvent" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:352:69 - error: "result" 的类型部分未知
    "result" 为 "Unknown | str | None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:352:69 - error: `None` 不支持下标访问 (reportOptionalSubscript)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:352:77 - error: 无法访问 "UserMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:352:77 - error: 无法访问 "AssistantMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:352:77 - error: 无法访问 "SystemMessage" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:352:77 - error: 无法访问 "StreamEvent" 类的 "result" 属性
    属性 "result" 未知 (reportAttributeAccessIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:13:37 - error: "Optional" 导入项未使用 (reportUnusedImport)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:617:16 - error: "subprocess" 可能未绑定 (reportPossiblyUnboundVariable)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:316:24 - error: 变量 "title" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:514:17 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:527:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:544:25 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:548:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:555:17 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:558:51 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:559:20 - error: 返回类型 "tuple[Literal[False], list[Unknown]]" 部分未知 (reportUnknownVariableType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:20:24 - error: "state_manager" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21:9 - error: "state_manager" 类型未知 (reportUnknownMemberType)
32 errors, 0 warnings, 0 notes
```


# BasedPyright 检查报告
**生成时间**: 2026-01-06 10:15:06
**检查时间**: 2026-01-06T10:15:06.139627
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 12 |
| ❌ 错误 (Error) | 35 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.06 秒 |

## 🔴 错误详情

共发现 **35** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py`: 35 个错误

### 按规则分组

- `reportUnknownMemberType`: 10 次
- `reportUnknownArgumentType`: 8 次
- `reportUnnecessaryIsInstance`: 4 次
- `reportArgumentType`: 4 次
- `reportUnknownVariableType`: 4 次
- `reportAttributeAccessIssue`: 3 次
- `reportUnusedImport`: 1 次
- `reportUnnecessaryCast`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:11

- **规则**: `reportUnusedImport`
- **位置**: 第 11 行, 第 46 列
- **错误信息**: "Union" 导入项未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:127

- **规则**: `reportUnnecessaryIsInstance`
- **位置**: 第 127 行, 第 23 列
- **错误信息**: "list[ContentBlock]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance`

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:154

- **规则**: `reportUnnecessaryIsInstance`
- **位置**: 第 154 行, 第 52 列
- **错误信息**: "dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance`

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:173

- **规则**: `reportArgumentType`
- **位置**: 第 173 行, 第 41 列
- **错误信息**: "type[ResultMessage] | None" 类型的实参无法赋值给函数 "isinstance" 中 "_ClassInfo" 类型的形参 "class_or_tuple"
  "type[ResultMessage] | None" 类型与 "_ClassInfo" 类型不兼容
    "None" 类型与 "_ClassInfo" 类型不兼容
      "None" 与 "type" 不兼容
      "None" 与 "tuple[_ClassInfo, ...]" 不兼容

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:173

- **规则**: `reportArgumentType`
- **位置**: 第 173 行, 第 41 列
- **错误信息**: `isinstance` 的第二个参数必须是单个类或由多个类构成的元组
  `None` 不能参与 `isinstance()` 或 `issubclass()`

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:175

- **规则**: `reportUnknownMemberType`
- **位置**: 第 175 行, 第 27 列
- **错误信息**: "is_error" 的类型部分未知
  "is_error" 为 "Any | Unknown" 类型

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:175

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 175 行, 第 35 列
- **错误信息**: 无法访问 "AssistantMessage" 类的 "is_error" 属性
  属性 "is_error" 未知

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:175

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 175 行, 第 35 列
- **错误信息**: 无法访问 "SystemMessage" 类的 "is_error" 属性
  属性 "is_error" 未知

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:175

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 175 行, 第 35 列
- **错误信息**: 无法访问 "UserMessage" 类的 "is_error" 属性
  属性 "is_error" 未知

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:210

- **规则**: `reportUnknownVariableType`
- **位置**: 第 210 行, 第 24 列
- **错误信息**: "block" 类型未知

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:210

- **规则**: `reportUnknownMemberType`
- **位置**: 第 210 行, 第 33 列
- **错误信息**: "content" 的类型部分未知
  "content" 为 "list[Unknown]" 类型

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:211

- **规则**: `reportUnknownVariableType`
- **位置**: 第 211 行, 第 24 列
- **错误信息**: "block_type" 类型未知

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:211

- **规则**: `reportUnknownMemberType`
- **位置**: 第 211 行, 第 37 列
- **错误信息**: "__class__" 类型未知

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:211

- **规则**: `reportUnknownMemberType`
- **位置**: 第 211 行, 第 37 列
- **错误信息**: "__name__" 类型未知

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:212

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 212 行, 第 65 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:212

- **规则**: `reportUnknownMemberType`
- **位置**: 第 212 行, 第 84 列
- **错误信息**: "text" 类型未知

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:214

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 214 行, 第 71 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:214

- **规则**: `reportUnknownMemberType`
- **位置**: 第 214 行, 第 94 列
- **错误信息**: "thinking" 类型未知

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:219

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 219 行, 第 70 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:220

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 220 行, 第 58 列
- **错误信息**: 参数类型未知
  实参对应于 "getattr" 函数中的 "o" 形参

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:222

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 222 行, 第 73 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:223

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 223 行, 第 51 列
- **错误信息**: 参数类型未知
  实参对应于 "getattr" 函数中的 "o" 形参

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:228

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 228 行, 第 85 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:250

- **规则**: `reportUnnecessaryCast`
- **位置**: 第 250 行, 第 37 列
- **错误信息**: 当前已为 "str" 类型，不需要调用 `cast`

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:252

- **规则**: `reportUnknownMemberType`
- **位置**: 第 252 行, 第 45 列
- **错误信息**: "content" 的类型部分未知
  "content" 为 "list[Unknown]" 类型

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:252

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 252 行, 第 45 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:263

- **规则**: `reportUnnecessaryIsInstance`
- **位置**: 第 263 行, 第 27 列
- **错误信息**: "str" 一定是 "str" 的实例，无需再调用 `isinstance`

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:294

- **规则**: `reportUnnecessaryIsInstance`
- **位置**: 第 294 行, 第 55 列
- **错误信息**: "list[ContentBlock]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance`

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:309

- **规则**: `reportArgumentType`
- **位置**: 第 309 行, 第 41 列
- **错误信息**: "type[ResultMessage] | None" 类型的实参无法赋值给函数 "isinstance" 中 "_ClassInfo" 类型的形参 "class_or_tuple"
  "type[ResultMessage] | None" 类型与 "_ClassInfo" 类型不兼容
    "None" 类型与 "_ClassInfo" 类型不兼容
      "None" 与 "type" 不兼容
      "None" 与 "tuple[_ClassInfo, ...]" 不兼容

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:309

- **规则**: `reportArgumentType`
- **位置**: 第 309 行, 第 41 列
- **错误信息**: `isinstance` 的第二个参数必须是单个类或由多个类构成的元组
  `None` 不能参与 `isinstance()` 或 `issubclass()`

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:330

- **规则**: `reportUnknownVariableType`
- **位置**: 第 330 行, 第 28 列
- **错误信息**: "block" 类型未知

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:330

- **规则**: `reportUnknownMemberType`
- **位置**: 第 330 行, 第 37 列
- **错误信息**: "content" 的类型部分未知
  "content" 为 "list[Unknown]" 类型

#### 33. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:331

- **规则**: `reportUnknownVariableType`
- **位置**: 第 331 行, 第 28 列
- **错误信息**: "block_type" 类型未知

#### 34. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:331

- **规则**: `reportUnknownMemberType`
- **位置**: 第 331 行, 第 41 列
- **错误信息**: "__class__" 类型未知

#### 35. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:331

- **规则**: `reportUnknownMemberType`
- **位置**: 第 331 行, 第 41 列
- **错误信息**: "__name__" 类型未知

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\agents.py`
3. `..\autoBMAD\epic_automation\code_quality_agent.py`
4. `..\autoBMAD\epic_automation\dev_agent.py`
5. `..\autoBMAD\epic_automation\epic_driver.py`
6. `..\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py`
7. `..\autoBMAD\epic_automation\qa_agent.py`
8. `..\autoBMAD\epic_automation\qa_tools_integration.py`
9. `..\autoBMAD\epic_automation\sdk_wrapper.py`
10. `..\autoBMAD\epic_automation\sm_agent.py`
11. `..\autoBMAD\epic_automation\state_manager.py`
12. `..\autoBMAD\epic_automation\test_automation_agent.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:11:47 - error: "Union" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:127:24 - error: "list[ContentBlock]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:154:53 - error: "dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:173:42 - error: "type[ResultMessage] | None" 类型的实参无法赋值给函数 "isinstance" 中 "_ClassInfo" 类型的形参 "class_or_tuple"
    "type[ResultMessage] | None" 类型与 "_ClassInfo" 类型不兼容
      "None" 类型与 "_ClassInfo" 类型不兼容
        "None" 与 "type" 不兼容
        "None" 与 "tuple[_ClassInfo, ...]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:173:42 - error: `isinstance` 的第二个参数必须是单个类或由多个类构成的元组
    `None` 不能参与 `isinstance()` 或 `issubclass()` (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:175:28 - error: "is_error" 的类型部分未知
    "is_error" 为 "Any | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:175:36 - error: 无法访问 "AssistantMessage" 类的 "is_error" 属性
    属性 "is_error" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:175:36 - error: 无法访问 "SystemMessage" 类的 "is_error" 属性
    属性 "is_error" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:175:36 - error: 无法访问 "UserMessage" 类的 "is_error" 属性
    属性 "is_error" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:210:25 - error: "block" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:210:34 - error: "content" 的类型部分未知
    "content" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:211:25 - error: "block_type" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:211:38 - error: "__class__" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:211:38 - error: "__name__" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:212:66 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:212:85 - error: "text" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:214:72 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:214:95 - error: "thinking" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:219:71 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:220:59 - error: 参数类型未知
    实参对应于 "getattr" 函数中的 "o" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:222:74 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:223:52 - error: 参数类型未知
    实参对应于 "getattr" 函数中的 "o" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:228:86 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:250:38 - error: 当前已为 "str" 类型，不需要调用 `cast` (reportUnnecessaryCast)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:252:46 - error: "content" 的类型部分未知
    "content" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:252:46 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:263:28 - error: "str" 一定是 "str" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:294:56 - error: "list[ContentBlock]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:309:42 - error: "type[ResultMessage] | None" 类型的实参无法赋值给函数 "isinstance" 中 "_ClassInfo" 类型的形参 "class_or_tuple"
    "type[ResultMessage] | None" 类型与 "_ClassInfo" 类型不兼容
      "None" 类型与 "_ClassInfo" 类型不兼容
        "None" 与 "type" 不兼容
        "None" 与 "tuple[_ClassInfo, ...]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:309:42 - error: `isinstance` 的第二个参数必须是单个类或由多个类构成的元组
    `None` 不能参与 `isinstance()` 或 `issubclass()` (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:330:29 - error: "block" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:330:38 - error: "content" 的类型部分未知
    "content" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:331:29 - error: "block_type" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:331:42 - error: "__class__" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:331:42 - error: "__name__" 类型未知 (reportUnknownMemberType)
35 errors, 0 warnings, 0 notes
```


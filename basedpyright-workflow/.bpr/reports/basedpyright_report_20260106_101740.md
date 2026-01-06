# BasedPyright 检查报告
**生成时间**: 2026-01-06 10:17:40
**检查时间**: 2026-01-06T10:17:40.340271
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 12 |
| ❌ 错误 (Error) | 24 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.02 秒 |

## 🔴 错误详情

共发现 **24** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py`: 24 个错误

### 按规则分组

- `reportUnknownMemberType`: 9 次
- `reportUnknownArgumentType`: 8 次
- `reportUnknownVariableType`: 4 次
- `reportUnnecessaryIsInstance`: 3 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:127

- **规则**: `reportUnnecessaryIsInstance`
- **位置**: 第 127 行, 第 23 列
- **错误信息**: "list[ContentBlock]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance`

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:154

- **规则**: `reportUnnecessaryIsInstance`
- **位置**: 第 154 行, 第 52 列
- **错误信息**: "dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance`

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:210

- **规则**: `reportUnknownVariableType`
- **位置**: 第 210 行, 第 24 列
- **错误信息**: "block" 类型未知

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:210

- **规则**: `reportUnknownMemberType`
- **位置**: 第 210 行, 第 33 列
- **错误信息**: "content" 的类型部分未知
  "content" 为 "list[Unknown]" 类型

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:211

- **规则**: `reportUnknownVariableType`
- **位置**: 第 211 行, 第 24 列
- **错误信息**: "block_type" 类型未知

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:211

- **规则**: `reportUnknownMemberType`
- **位置**: 第 211 行, 第 42 列
- **错误信息**: "__class__" 类型未知

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:211

- **规则**: `reportUnknownMemberType`
- **位置**: 第 211 行, 第 42 列
- **错误信息**: "__name__" 类型未知

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:212

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 212 行, 第 65 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:212

- **规则**: `reportUnknownMemberType`
- **位置**: 第 212 行, 第 84 列
- **错误信息**: "text" 类型未知

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:214

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 214 行, 第 71 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:214

- **规则**: `reportUnknownMemberType`
- **位置**: 第 214 行, 第 94 列
- **错误信息**: "thinking" 类型未知

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:219

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 219 行, 第 70 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:220

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 220 行, 第 58 列
- **错误信息**: 参数类型未知
  实参对应于 "getattr" 函数中的 "o" 形参

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:222

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 222 行, 第 73 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:223

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 223 行, 第 51 列
- **错误信息**: 参数类型未知
  实参对应于 "getattr" 函数中的 "o" 形参

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:228

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 228 行, 第 85 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:252

- **规则**: `reportUnknownMemberType`
- **位置**: 第 252 行, 第 45 列
- **错误信息**: "content" 的类型部分未知
  "content" 为 "list[Unknown]" 类型

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:252

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 252 行, 第 45 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:294

- **规则**: `reportUnnecessaryIsInstance`
- **位置**: 第 294 行, 第 55 列
- **错误信息**: "list[ContentBlock]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance`

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:330

- **规则**: `reportUnknownVariableType`
- **位置**: 第 330 行, 第 28 列
- **错误信息**: "block" 类型未知

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:330

- **规则**: `reportUnknownMemberType`
- **位置**: 第 330 行, 第 37 列
- **错误信息**: "content" 的类型部分未知
  "content" 为 "list[Unknown]" 类型

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:331

- **规则**: `reportUnknownVariableType`
- **位置**: 第 331 行, 第 28 列
- **错误信息**: "block_type" 类型未知

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:331

- **规则**: `reportUnknownMemberType`
- **位置**: 第 331 行, 第 46 列
- **错误信息**: "__class__" 类型未知

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:331

- **规则**: `reportUnknownMemberType`
- **位置**: 第 331 行, 第 46 列
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
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:127:24 - error: "list[ContentBlock]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:154:53 - error: "dict[str, Any]" 一定是 "dict[Unknown, Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:210:25 - error: "block" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:210:34 - error: "content" 的类型部分未知
    "content" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:211:25 - error: "block_type" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:211:43 - error: "__class__" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:211:43 - error: "__name__" 类型未知 (reportUnknownMemberType)
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
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:252:46 - error: "content" 的类型部分未知
    "content" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:252:46 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:294:56 - error: "list[ContentBlock]" 一定是 "list[Unknown]" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:330:29 - error: "block" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:330:38 - error: "content" 的类型部分未知
    "content" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:331:29 - error: "block_type" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:331:47 - error: "__class__" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:331:47 - error: "__name__" 类型未知 (reportUnknownMemberType)
24 errors, 0 warnings, 0 notes
```


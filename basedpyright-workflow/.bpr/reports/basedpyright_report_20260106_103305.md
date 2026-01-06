# BasedPyright 检查报告
**生成时间**: 2026-01-06 10:33:05
**检查时间**: 2026-01-06T10:33:05.475645
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 12 |
| ❌ 错误 (Error) | 79 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.02 秒 |

## 🔴 错误详情

共发现 **79** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py`: 79 个错误

### 按规则分组

- `reportUnknownMemberType`: 27 次
- `reportUnknownVariableType`: 18 次
- `reportUnknownArgumentType`: 15 次
- `reportGeneralTypeIssues`: 6 次
- `reportRedeclaration`: 6 次
- `reportIndexIssue`: 3 次
- `reportUnusedVariable`: 2 次
- `reportUnusedImport`: 1 次
- `reportUndefinedVariable`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:11

- **规则**: `reportUnusedImport`
- **位置**: 第 11 行, 第 24 列
- **错误信息**: "List" 导入项未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:63

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 63 行, 第 33 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:68

- **规则**: `reportUndefinedVariable`
- **位置**: 第 68 行, 第 28 列
- **错误信息**: "Optional" 未定义

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:87

- **规则**: `reportUnknownMemberType`
- **位置**: 第 87 行, 第 11 列
- **错误信息**: "_display_task" 类型未知

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:88

- **规则**: `reportUnknownMemberType`
- **位置**: 第 88 行, 第 18 列
- **错误信息**: "_display_task" 类型未知

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:122

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 122 行, 第 65 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:125

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 125 行, 第 28 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:129

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 129 行, 第 60 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:138

- **规则**: `reportUnknownVariableType`
- **位置**: 第 138 行, 第 28 列
- **错误信息**: "block" 类型未知

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:138

- **规则**: `reportUnknownMemberType`
- **位置**: 第 138 行, 第 37 列
- **错误信息**: "content" 的类型部分未知
  "content" 为 "list[Unknown]" 类型

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:139

- **规则**: `reportUnknownVariableType`
- **位置**: 第 139 行, 第 28 列
- **错误信息**: "block_obj" 类型未知

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:139

- **规则**: `reportRedeclaration`
- **位置**: 第 139 行, 第 28 列
- **错误信息**: "block_obj" 变量声明被同名声明遮蔽

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:140

- **规则**: `reportUnknownVariableType`
- **位置**: 第 140 行, 第 28 列
- **错误信息**: "block_obj" 类型未知

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:141

- **规则**: `reportUnknownMemberType`
- **位置**: 第 141 行, 第 94 列
- **错误信息**: "text" 的类型部分未知
  "text" 为 "Unknown | Any" 类型

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:142

- **规则**: `reportUnknownVariableType`
- **位置**: 第 142 行, 第 32 列
- **错误信息**: "text_content" 的类型部分未知
  "text_content" 为 "Unknown | Any" 类型

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:142

- **规则**: `reportUnknownMemberType`
- **位置**: 第 142 行, 第 52 列
- **错误信息**: "text" 的类型部分未知
  "text" 为 "Unknown | Any" 类型

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:142

- **规则**: `reportUnknownMemberType`
- **位置**: 第 142 行, 第 52 列
- **错误信息**: "strip" 的类型部分未知
  "strip" 为 "Unknown | Any" 类型

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:143

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 143 行, 第 53 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "append" 函数中的 "object" 形参
  参数类型为 "Unknown | str"

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:144

- **规则**: `reportUnknownMemberType`
- **位置**: 第 144 行, 第 100 列
- **错误信息**: "thinking" 类型未知

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:146

- **规则**: `reportUnknownVariableType`
- **位置**: 第 146 行, 第 32 列
- **错误信息**: "thinking_text" 类型未知

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:146

- **规则**: `reportUnknownMemberType`
- **位置**: 第 146 行, 第 48 列
- **错误信息**: "thinking" 类型未知

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:146

- **规则**: `reportUnknownMemberType`
- **位置**: 第 146 行, 第 48 列
- **错误信息**: "strip" 类型未知

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:147

- **规则**: `reportUnknownVariableType`
- **位置**: 第 147 行, 第 32 列
- **错误信息**: "preview" 类型未知

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:147

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 147 行, 第 82 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:149

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 149 行, 第 106 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:150

- **规则**: `reportRedeclaration`
- **位置**: 第 150 行, 第 32 列
- **错误信息**: "tool_name" 变量声明被同名声明遮蔽

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:150

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 150 行, 第 67 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "getattr" 函数中的 "o" 形参
  参数类型为 "Unknown | Any"

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:152

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 152 行, 第 112 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:153

- **规则**: `reportUnknownVariableType`
- **位置**: 第 153 行, 第 32 列
- **错误信息**: "tool_content" 的类型部分未知
  "tool_content" 为 "Unknown | Any" 类型

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:153

- **规则**: `reportUnknownMemberType`
- **位置**: 第 153 行, 第 52 列
- **错误信息**: "content" 的类型部分未知
  "content" 为 "Unknown | Any" 类型

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:158

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 158 行, 第 89 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:169

- **规则**: `reportUnknownMemberType`
- **位置**: 第 169 行, 第 56 列
- **错误信息**: "data" 的类型部分未知
  "data" 为 "dict[Unknown, Unknown]" 类型

#### 33. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:169

- **规则**: `reportUnknownMemberType`
- **位置**: 第 169 行, 第 56 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 34. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:170

- **规则**: `reportUnknownMemberType`
- **位置**: 第 170 行, 第 51 列
- **错误信息**: "data" 的类型部分未知
  "data" 为 "dict[Unknown, Unknown]" 类型

#### 35. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:170

- **规则**: `reportUnknownMemberType`
- **位置**: 第 170 行, 第 51 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 36. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:173

- **规则**: `reportUnknownMemberType`
- **位置**: 第 173 行, 第 55 列
- **错误信息**: "data" 的类型部分未知
  "data" 为 "dict[Unknown, Unknown]" 类型

#### 37. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:173

- **规则**: `reportUnknownMemberType`
- **位置**: 第 173 行, 第 55 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 38. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:182

- **规则**: `reportUnknownMemberType`
- **位置**: 第 182 行, 第 49 列
- **错误信息**: "content" 的类型部分未知
  "content" 为 "list[Unknown]" 类型

#### 39. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:182

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 182 行, 第 49 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 40. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:213

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 213 行, 第 69 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 41. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:222

- **规则**: `reportUnknownVariableType`
- **位置**: 第 222 行, 第 24 列
- **错误信息**: "block" 类型未知

#### 42. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:222

- **规则**: `reportUnknownMemberType`
- **位置**: 第 222 行, 第 33 列
- **错误信息**: "content" 的类型部分未知
  "content" 为 "list[Unknown]" 类型

#### 43. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:223

- **规则**: `reportUnknownVariableType`
- **位置**: 第 223 行, 第 24 列
- **错误信息**: "block_obj" 类型未知

#### 44. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:223

- **规则**: `reportUnusedVariable`
- **位置**: 第 223 行, 第 24 列
- **错误信息**: 变量 "block_obj" 未使用

#### 45. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:223

- **规则**: `reportRedeclaration`
- **位置**: 第 223 行, 第 24 列
- **错误信息**: "block_obj" 变量声明被同名声明遮蔽

#### 46. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:224

- **规则**: `reportUnknownVariableType`
- **位置**: 第 224 行, 第 24 列
- **错误信息**: "block_obj" 类型未知

#### 47. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:224

- **规则**: `reportUnusedVariable`
- **位置**: 第 224 行, 第 24 列
- **错误信息**: 变量 "block_obj" 未使用

#### 48. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:225

- **规则**: `reportUnknownVariableType`
- **位置**: 第 225 行, 第 24 列
- **错误信息**: "block_type" 类型未知

#### 49. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:225

- **规则**: `reportUnknownMemberType`
- **位置**: 第 225 行, 第 42 列
- **错误信息**: "__class__" 类型未知

#### 50. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:225

- **规则**: `reportUnknownMemberType`
- **位置**: 第 225 行, 第 42 列
- **错误信息**: "__name__" 类型未知

#### 51. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:226

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 226 行, 第 65 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 52. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:226

- **规则**: `reportUnknownMemberType`
- **位置**: 第 226 行, 第 84 列
- **错误信息**: "text" 类型未知

#### 53. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:228

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 228 行, 第 71 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 54. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:228

- **规则**: `reportUnknownMemberType`
- **位置**: 第 228 行, 第 94 列
- **错误信息**: "thinking" 类型未知

#### 55. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:233

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 233 行, 第 70 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 56. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:234

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 234 行, 第 58 列
- **错误信息**: 参数类型未知
  实参对应于 "getattr" 函数中的 "o" 形参

#### 57. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:236

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 236 行, 第 73 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 58. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:237

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 237 行, 第 51 列
- **错误信息**: 参数类型未知
  实参对应于 "getattr" 函数中的 "o" 形参

#### 59. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:242

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 242 行, 第 85 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 60. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:253

- **规则**: `reportIndexIssue`
- **位置**: 第 253 行, 第 42 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 61. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:254

- **规则**: `reportIndexIssue`
- **位置**: 第 254 行, 第 37 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 62. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:257

- **规则**: `reportIndexIssue`
- **位置**: 第 257 行, 第 41 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 63. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:266

- **规则**: `reportUnknownMemberType`
- **位置**: 第 266 行, 第 45 列
- **错误信息**: "content" 的类型部分未知
  "content" 为 "list[Unknown]" 类型

#### 64. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:266

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 266 行, 第 45 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 65. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:309

- **规则**: `reportUnknownVariableType`
- **位置**: 第 309 行, 第 28 列
- **错误信息**: "block" 类型未知

#### 66. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:309

- **规则**: `reportUnknownMemberType`
- **位置**: 第 309 行, 第 37 列
- **错误信息**: "content" 的类型部分未知
  "content" 为 "list[Unknown]" 类型

#### 67. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:310

- **规则**: `reportUnknownVariableType`
- **位置**: 第 310 行, 第 28 列
- **错误信息**: "block_obj" 类型未知

#### 68. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:310

- **规则**: `reportRedeclaration`
- **位置**: 第 310 行, 第 28 列
- **错误信息**: "block_obj" 变量声明被同名声明遮蔽

#### 69. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:311

- **规则**: `reportUnknownVariableType`
- **位置**: 第 311 行, 第 28 列
- **错误信息**: "block_obj" 类型未知

#### 70. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:311

- **规则**: `reportRedeclaration`
- **位置**: 第 311 行, 第 28 列
- **错误信息**: "block_obj" 变量声明被同名声明遮蔽

#### 71. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:346

- **规则**: `reportUnknownVariableType`
- **位置**: 第 346 行, 第 28 列
- **错误信息**: "block" 类型未知

#### 72. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:346

- **规则**: `reportUnknownMemberType`
- **位置**: 第 346 行, 第 37 列
- **错误信息**: "content" 的类型部分未知
  "content" 为 "list[Unknown]" 类型

#### 73. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:347

- **规则**: `reportUnknownVariableType`
- **位置**: 第 347 行, 第 28 列
- **错误信息**: "block_obj" 类型未知

#### 74. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:347

- **规则**: `reportRedeclaration`
- **位置**: 第 347 行, 第 28 列
- **错误信息**: "block_obj" 变量声明被同名声明遮蔽

#### 75. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:348

- **规则**: `reportUnknownVariableType`
- **位置**: 第 348 行, 第 28 列
- **错误信息**: "block_obj" 类型未知

#### 76. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:349

- **规则**: `reportUnknownVariableType`
- **位置**: 第 349 行, 第 28 列
- **错误信息**: "block_type" 类型未知

#### 77. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:349

- **规则**: `reportUnknownMemberType`
- **位置**: 第 349 行, 第 46 列
- **错误信息**: "__class__" 类型未知

#### 78. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:349

- **规则**: `reportUnknownMemberType`
- **位置**: 第 349 行, 第 46 列
- **错误信息**: "__name__" 类型未知

#### 79. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:511

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 511 行, 第 19 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

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
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:11:25 - error: "List" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:63:34 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:68:29 - error: "Optional" 未定义 (reportUndefinedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:87:12 - error: "_display_task" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:88:19 - error: "_display_task" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:122:66 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:125:29 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:129:61 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:138:29 - error: "block" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:138:38 - error: "content" 的类型部分未知
    "content" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:139:29 - error: "block_obj" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:139:29 - error: "block_obj" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:140:29 - error: "block_obj" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:141:95 - error: "text" 的类型部分未知
    "text" 为 "Unknown | Any" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:142:33 - error: "text_content" 的类型部分未知
    "text_content" 为 "Unknown | Any" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:142:53 - error: "text" 的类型部分未知
    "text" 为 "Unknown | Any" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:142:53 - error: "strip" 的类型部分未知
    "strip" 为 "Unknown | Any" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:143:54 - error: 部分参数的类型未知
    实参对应于 "append" 函数中的 "object" 形参
    参数类型为 "Unknown | str" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:144:101 - error: "thinking" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:146:33 - error: "thinking_text" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:146:49 - error: "thinking" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:146:49 - error: "strip" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:147:33 - error: "preview" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:147:83 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:149:107 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:150:33 - error: "tool_name" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:150:68 - error: 部分参数的类型未知
    实参对应于 "getattr" 函数中的 "o" 形参
    参数类型为 "Unknown | Any" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:152:113 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:153:33 - error: "tool_content" 的类型部分未知
    "tool_content" 为 "Unknown | Any" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:153:53 - error: "content" 的类型部分未知
    "content" 为 "Unknown | Any" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:158:90 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:169:57 - error: "data" 的类型部分未知
    "data" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:169:57 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:170:52 - error: "data" 的类型部分未知
    "data" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:170:52 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:173:56 - error: "data" 的类型部分未知
    "data" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:173:56 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:182:50 - error: "content" 的类型部分未知
    "content" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:182:50 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:213:70 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:222:25 - error: "block" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:222:34 - error: "content" 的类型部分未知
    "content" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:223:25 - error: "block_obj" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:223:25 - error: 变量 "block_obj" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:223:25 - error: "block_obj" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:224:25 - error: "block_obj" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:224:25 - error: 变量 "block_obj" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:225:25 - error: "block_type" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:225:43 - error: "__class__" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:225:43 - error: "__name__" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:226:66 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:226:85 - error: "text" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:228:72 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:228:95 - error: "thinking" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:233:71 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:234:59 - error: 参数类型未知
    实参对应于 "getattr" 函数中的 "o" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:236:74 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:237:52 - error: 参数类型未知
    实参对应于 "getattr" 函数中的 "o" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:242:86 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:253:43 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:254:38 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:257:42 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:266:46 - error: "content" 的类型部分未知
    "content" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:266:46 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:309:29 - error: "block" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:309:38 - error: "content" 的类型部分未知
    "content" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:310:29 - error: "block_obj" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:310:29 - error: "block_obj" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:311:29 - error: "block_obj" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:311:29 - error: "block_obj" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:346:29 - error: "block" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:346:38 - error: "content" 的类型部分未知
    "content" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:347:29 - error: "block_obj" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:347:29 - error: "block_obj" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:348:29 - error: "block_obj" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:349:29 - error: "block_type" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:349:47 - error: "__class__" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:349:47 - error: "__name__" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sdk_wrapper.py:511:20 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
79 errors, 0 warnings, 0 notes
```


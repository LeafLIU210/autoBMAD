# BasedPyright 检查报告
**生成时间**: 2026-01-05 11:57:38
**检查时间**: 2026-01-05T11:57:38.162236
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 12 |
| ❌ 错误 (Error) | 410 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.60 秒 |

## 🔴 错误详情

共发现 **410** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 72 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py`: 71 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py`: 65 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py`: 52 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py`: 45 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py`: 27 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py`: 20 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py`: 19 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py`: 17 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py`: 12 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py`: 10 个错误

### 按规则分组

- `reportUnknownMemberType`: 130 次
- `reportUnknownVariableType`: 124 次
- `reportUnknownArgumentType`: 42 次
- `reportAttributeAccessIssue`: 25 次
- `reportIndexIssue`: 22 次
- `reportGeneralTypeIssues`: 20 次
- `reportUnknownParameterType`: 12 次
- `reportOptionalCall`: 6 次
- `reportMissingImports`: 6 次
- `reportUnusedVariable`: 5 次
- `reportArgumentType`: 5 次
- `reportUnusedImport`: 3 次
- `reportMissingParameterType`: 3 次
- `reportMissingTypeArgument`: 2 次
- `reportUnknownLambdaType`: 2 次
- `reportPossiblyUnboundVariable`: 1 次
- `reportAssignmentType`: 1 次
- `reportConstantRedefinition`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:19

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 19 行, 第 38 列
- **错误信息**: "run_basedpyright_check" 是未知的导入符号

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:19

- **规则**: `reportUnknownVariableType`
- **位置**: 第 19 行, 第 38 列
- **错误信息**: "run_basedpyright_check" 类型未知

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:20

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 20 行, 第 38 列
- **错误信息**: "run_ruff_check" 是未知的导入符号

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:20

- **规则**: `reportUnknownVariableType`
- **位置**: 第 20 行, 第 38 列
- **错误信息**: "run_ruff_check" 类型未知

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:28

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 28 行, 第 33 列
- **错误信息**: "Claude" 是未知的导入符号

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:28

- **规则**: `reportUnknownVariableType`
- **位置**: 第 28 行, 第 33 列
- **错误信息**: "Claude" 类型未知

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:28

- **规则**: `reportUnusedImport`
- **位置**: 第 28 行, 第 33 列
- **错误信息**: "Claude" 导入项未使用

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:76

- **规则**: `reportUnknownVariableType`
- **位置**: 第 76 行, 第 8 列
- **错误信息**: "results" 的类型部分未知
  "results" 为 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 类型

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:92

- **规则**: `reportUnknownMemberType`
- **位置**: 第 92 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "Unknown | ((object: Unknown, /) -> None)" 类型

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:92

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 92 行, 第 30 列
- **错误信息**: 无法访问 "str" 类的 "append" 属性
  属性 "append" 未知

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:92

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 92 行, 第 30 列
- **错误信息**: 无法访问 "int" 类的 "append" 属性
  属性 "append" 未知

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:92

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 92 行, 第 30 列
- **错误信息**: 无法访问 "dict[Unknown, Unknown]" 类的 "append" 属性
  属性 "append" 未知

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:93

- **规则**: `reportUnknownVariableType`
- **位置**: 第 93 行, 第 19 列
- **错误信息**: 返回类型 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 部分未知

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:102

- **规则**: `reportUnknownVariableType`
- **位置**: 第 102 行, 第 19 列
- **错误信息**: 返回类型 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 部分未知

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:129

- **规则**: `reportUnknownVariableType`
- **位置**: 第 129 行, 第 23 列
- **错误信息**: 返回类型 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 部分未知

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:150

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 150 行, 第 29 列
- **错误信息**: "total_errors" 可能未绑定

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:154

- **规则**: `reportUnknownVariableType`
- **位置**: 第 154 行, 第 15 列
- **错误信息**: 返回类型 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 部分未知

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:169

- **规则**: `reportUnknownVariableType`
- **位置**: 第 169 行, 第 12 列
- **错误信息**: "result" 类型未知

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:169

- **规则**: `reportOptionalCall`
- **位置**: 第 169 行, 第 27 列
- **错误信息**: `None` 不支持调用

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:174

- **规则**: `reportUnknownVariableType`
- **位置**: 第 174 行, 第 16 列
- **错误信息**: "file_errors" 类型未知

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:174

- **规则**: `reportUnknownMemberType`
- **位置**: 第 174 行, 第 30 列
- **错误信息**: "get" 类型未知

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:174

- **规则**: `reportUnknownMemberType`
- **位置**: 第 174 行, 第 30 列
- **错误信息**: "get" 类型未知

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:175

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 175 行, 第 34 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:177

- **规则**: `reportUnknownMemberType`
- **位置**: 第 177 行, 第 38 列
- **错误信息**: "get" 类型未知

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:187

- **规则**: `reportUnknownVariableType`
- **位置**: 第 187 行, 第 19 列
- **错误信息**: 返回类型未知

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:211

- **规则**: `reportUnknownVariableType`
- **位置**: 第 211 行, 第 12 列
- **错误信息**: "result" 类型未知

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:211

- **规则**: `reportOptionalCall`
- **位置**: 第 211 行, 第 27 列
- **错误信息**: `None` 不支持调用

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:216

- **规则**: `reportUnknownVariableType`
- **位置**: 第 216 行, 第 16 列
- **错误信息**: "file_errors" 类型未知

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:216

- **规则**: `reportUnknownMemberType`
- **位置**: 第 216 行, 第 30 列
- **错误信息**: "get" 类型未知

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:216

- **规则**: `reportUnknownMemberType`
- **位置**: 第 216 行, 第 30 列
- **错误信息**: "get" 类型未知

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:217

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 217 行, 第 34 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:219

- **规则**: `reportUnknownMemberType`
- **位置**: 第 219 行, 第 38 列
- **错误信息**: "get" 类型未知

#### 33. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:230

- **规则**: `reportUnknownVariableType`
- **位置**: 第 230 行, 第 19 列
- **错误信息**: 返回类型未知

#### 34. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:256

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 256 行, 第 45 列
- **错误信息**: "Claude" 是未知的导入符号

#### 35. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:256

- **规则**: `reportUnknownVariableType`
- **位置**: 第 256 行, 第 45 列
- **错误信息**: "Claude" 类型未知

#### 36. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:274

- **规则**: `reportUnknownVariableType`
- **位置**: 第 274 行, 第 12 列
- **错误信息**: "claude" 类型未知

#### 37. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:277

- **规则**: `reportUnusedVariable`
- **位置**: 第 277 行, 第 12 列
- **错误信息**: 变量 "fixed_files" 未使用

#### 38. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:285

- **规则**: `reportUnknownMemberType`
- **位置**: 第 285 行, 第 16 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 39. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:292

- **规则**: `reportUnknownMemberType`
- **位置**: 第 292 行, 第 16 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 40. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:299

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 299 行, 第 45 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "_create_fix_prompt" 函数中的 "errors" 形参
  参数类型为 "list[Unknown]"

#### 41. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:302

- **规则**: `reportUnknownVariableType`
- **位置**: 第 302 行, 第 12 列
- **错误信息**: "response" 类型未知

#### 42. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:302

- **规则**: `reportUnknownMemberType`
- **位置**: 第 302 行, 第 29 列
- **错误信息**: "messages" 类型未知

#### 43. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:302

- **规则**: `reportUnknownMemberType`
- **位置**: 第 302 行, 第 29 列
- **错误信息**: "create" 类型未知

#### 44. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:315

- **规则**: `reportUnknownMemberType`
- **位置**: 第 315 行, 第 15 列
- **错误信息**: "content" 类型未知

#### 45. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:316

- **规则**: `reportUnknownMemberType`
- **位置**: 第 316 行, 第 53 列
- **错误信息**: "content" 类型未知

#### 46. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:151

- **规则**: `reportUnknownVariableType`
- **位置**: 第 151 行, 第 12 列
- **错误信息**: "requirements" 的类型部分未知
  "requirements" 为 "dict[str, str | list[Unknown] | dict[Unknown, Unknown]]" 类型

#### 47. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:171

- **规则**: `reportUnknownVariableType`
- **位置**: 第 171 行, 第 24 列
- **错误信息**: "acceptance_criteria" 的类型部分未知
  "acceptance_criteria" 为 "str | list[Unknown] | dict[Unknown, Unknown]" 类型

#### 48. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:173

- **规则**: `reportUnknownMemberType`
- **位置**: 第 173 行, 第 24 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 49. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:181

- **规则**: `reportUnknownVariableType`
- **位置**: 第 181 行, 第 24 列
- **错误信息**: "tasks" 的类型部分未知
  "tasks" 为 "str | list[Unknown] | dict[Unknown, Unknown]" 类型

#### 50. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:183

- **规则**: `reportUnknownMemberType`
- **位置**: 第 183 行, 第 24 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 51. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:189

- **规则**: `reportUnknownVariableType`
- **位置**: 第 189 行, 第 20 列
- **错误信息**: "subtasks" 的类型部分未知
  "subtasks" 为 "str | list[Unknown] | dict[Unknown, Unknown]" 类型

#### 52. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:191

- **规则**: `reportUnknownMemberType`
- **位置**: 第 191 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 53. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:196

- **规则**: `reportUnknownVariableType`
- **位置**: 第 196 行, 第 16 列
- **错误信息**: "dev_notes" 的类型部分未知
  "dev_notes" 为 "str | list[Unknown] | dict[Unknown, Unknown]" 类型

#### 54. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:203

- **规则**: `reportUnknownVariableType`
- **位置**: 第 203 行, 第 16 列
- **错误信息**: "testing" 的类型部分未知
  "testing" 为 "str | list[Unknown] | dict[Unknown, Unknown]" 类型

#### 55. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:207

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 207 行, 第 55 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "str | list[Unknown] | dict[Unknown, Unknown]"

#### 56. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:207

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 207 行, 第 102 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "str | list[Unknown] | dict[Unknown, Unknown]"

#### 57. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:207

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 207 行, 第 138 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "str | list[Unknown] | dict[Unknown, Unknown]"

#### 58. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:208

- **规则**: `reportUnknownVariableType`
- **位置**: 第 208 行, 第 19 列
- **错误信息**: 返回类型 "dict[str, str | list[Unknown] | dict[Unknown, Unknown]]" 部分未知

#### 59. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:220

- **规则**: `reportUnknownMemberType`
- **位置**: 第 220 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 60. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:223

- **规则**: `reportUnknownMemberType`
- **位置**: 第 223 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 61. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:227

- **规则**: `reportUnknownMemberType`
- **位置**: 第 227 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 62. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:230

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 230 行, 第 25 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 63. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:31

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 31 行, 第 13 列
- **错误信息**: "list" 泛型类应有类型参数

#### 64. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:42

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 42 行, 第 19 列
- **错误信息**: "dict" 泛型类应有类型参数

#### 65. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:142

- **规则**: `reportIndexIssue`
- **位置**: 第 142 行, 第 28 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 66. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:142

- **规则**: `reportIndexIssue`
- **位置**: 第 142 行, 第 33 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 67. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:211

- **规则**: `reportUnknownVariableType`
- **位置**: 第 211 行, 第 24 列
- **错误信息**: "story_file" 类型未知

#### 68. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:212

- **规则**: `reportUnknownMemberType`
- **位置**: 第 212 行, 第 24 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 69. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:214

- **规则**: `reportUnknownMemberType`
- **位置**: 第 214 行, 第 40 列
- **错误信息**: "resolve" 类型未知

#### 70. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:214

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 214 行, 第 40 列
- **错误信息**: 参数类型未知
  实参对应于 "__new__" 函数中的 "object" 形参

#### 71. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:215

- **规则**: `reportUnknownMemberType`
- **位置**: 第 215 行, 第 36 列
- **错误信息**: "name" 类型未知

#### 72. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:217

- **规则**: `reportUnknownMemberType`
- **位置**: 第 217 行, 第 24 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 73. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:225

- **规则**: `reportUnknownMemberType`
- **位置**: 第 225 行, 第 28 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 74. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:230

- **规则**: `reportUnknownMemberType`
- **位置**: 第 230 行, 第 28 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 75. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:242

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 242 行, 第 51 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__init__" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

#### 76. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:247

- **规则**: `reportUnknownMemberType`
- **位置**: 第 247 行, 第 12 列
- **错误信息**: "sort" 的类型部分未知
  "sort" 为 "Overload[(*, key: None = None, reverse: bool = False) -> None, (*, key: (Unknown) -> (SupportsDunderLT[Any] | SupportsDunderGT[Any]), reverse: bool = False) -> None]" 类型

#### 77. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:247

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 247 行, 第 36 列
- **错误信息**: "x" 参数的类型未知

#### 78. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:247

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 247 行, 第 39 列
- **错误信息**: 该 `lambda` 的返回类型未知

#### 79. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:250

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 250 行, 第 54 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 80. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:252

- **规则**: `reportUnknownVariableType`
- **位置**: 第 252 行, 第 19 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 81. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:260

- **规则**: `reportIndexIssue`
- **位置**: 第 260 行, 第 60 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 82. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:281

- **规则**: `reportUnknownMemberType`
- **位置**: 第 281 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 83. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:291

- **规则**: `reportUnknownMemberType`
- **位置**: 第 291 行, 第 16 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 84. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:295

- **规则**: `reportUnknownVariableType`
- **位置**: 第 295 行, 第 8 列
- **错误信息**: "seen" 的类型部分未知
  "seen" 为 "set[Unknown]" 类型

#### 85. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:297

- **规则**: `reportUnknownVariableType`
- **位置**: 第 297 行, 第 12 列
- **错误信息**: "story_id" 类型未知

#### 86. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:299

- **规则**: `reportUnknownVariableType`
- **位置**: 第 299 行, 第 12 列
- **错误信息**: "key" 类型未知

#### 87. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:299

- **规则**: `reportUnknownMemberType`
- **位置**: 第 299 行, 第 18 列
- **错误信息**: "split" 类型未知

#### 88. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:299

- **规则**: `reportUnknownMemberType`
- **位置**: 第 299 行, 第 18 列
- **错误信息**: "strip" 类型未知

#### 89. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:299

- **规则**: `reportUnknownMemberType`
- **位置**: 第 299 行, 第 18 列
- **错误信息**: "zfill" 类型未知

#### 90. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:301

- **规则**: `reportUnknownMemberType`
- **位置**: 第 301 行, 第 16 列
- **错误信息**: "add" 的类型部分未知
  "add" 为 "(element: Unknown, /) -> None" 类型

#### 91. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:301

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 301 行, 第 25 列
- **错误信息**: 参数类型未知
  实参对应于 "add" 函数中的 "element" 形参

#### 92. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:302

- **规则**: `reportUnknownMemberType`
- **位置**: 第 302 行, 第 16 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 93. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:302

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 302 行, 第 40 列
- **错误信息**: 参数类型未知
  实参对应于 "append" 函数中的 "object" 形参

#### 94. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:304

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 304 行, 第 38 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 95. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:306

- **规则**: `reportUnknownVariableType`
- **位置**: 第 306 行, 第 15 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 96. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:436

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 436 行, 第 88 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 97. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:557

- **规则**: `reportUnknownVariableType`
- **位置**: 第 557 行, 第 12 列
- **错误信息**: "guidance" 类型未知

#### 98. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:557

- **规则**: `reportUnknownMemberType`
- **位置**: 第 557 行, 第 23 列
- **错误信息**: "task_guidance" 的类型部分未知
  "task_guidance" 为 "dict[Unknown, Unknown]" 类型

#### 99. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:557

- **规则**: `reportUnknownMemberType`
- **位置**: 第 557 行, 第 23 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 100. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:610

- **规则**: `reportUnknownVariableType`
- **位置**: 第 610 行, 第 12 列
- **错误信息**: "guidance" 类型未知

#### 101. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:610

- **规则**: `reportUnknownMemberType`
- **位置**: 第 610 行, 第 23 列
- **错误信息**: "task_guidance" 的类型部分未知
  "task_guidance" 为 "dict[Unknown, Unknown]" 类型

#### 102. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:610

- **规则**: `reportUnknownMemberType`
- **位置**: 第 610 行, 第 23 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 103. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:656

- **规则**: `reportUnknownVariableType`
- **位置**: 第 656 行, 第 12 列
- **错误信息**: "guidance" 类型未知

#### 104. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:656

- **规则**: `reportUnknownMemberType`
- **位置**: 第 656 行, 第 23 列
- **错误信息**: "task_guidance" 的类型部分未知
  "task_guidance" 为 "dict[Unknown, Unknown]" 类型

#### 105. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:656

- **规则**: `reportUnknownMemberType`
- **位置**: 第 656 行, 第 23 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 106. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:699

- **规则**: `reportIndexIssue`
- **位置**: 第 699 行, 第 41 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 107. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:764

- **规则**: `reportIndexIssue`
- **位置**: 第 764 行, 第 53 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 108. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:764

- **规则**: `reportIndexIssue`
- **位置**: 第 764 行, 第 58 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 109. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:799

- **规则**: `reportIndexIssue`
- **位置**: 第 799 行, 第 45 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 110. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:815

- **规则**: `reportMissingImports`
- **位置**: 第 815 行, 第 17 列
- **错误信息**: 无法解析导入 "code_quality_agent"

#### 111. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:815

- **规则**: `reportUnknownVariableType`
- **位置**: 第 815 行, 第 43 列
- **错误信息**: "CodeQualityAgent" 类型未知

#### 112. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:817

- **规则**: `reportUnknownVariableType`
- **位置**: 第 817 行, 第 12 列
- **错误信息**: "quality_agent" 类型未知

#### 113. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:823

- **规则**: `reportUnknownVariableType`
- **位置**: 第 823 行, 第 12 列
- **错误信息**: "quality_results" 类型未知

#### 114. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:823

- **规则**: `reportUnknownMemberType`
- **位置**: 第 823 行, 第 36 列
- **错误信息**: "run_quality_gates" 类型未知

#### 115. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:829

- **规则**: `reportUnknownVariableType`
- **位置**: 第 829 行, 第 12 列
- **错误信息**: "status" 类型未知

#### 116. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:829

- **规则**: `reportUnknownMemberType`
- **位置**: 第 829 行, 第 21 列
- **错误信息**: "get" 类型未知

#### 117. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:830

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 830 行, 第 57 列
- **错误信息**: 参数类型未知
  实参对应于 "_update_progress" 函数中的 "status" 形参

#### 118. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:830

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 830 行, 第 65 列
- **错误信息**: 参数类型未知
  实参对应于 "_update_progress" 函数中的 "details" 形参

#### 119. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:839

- **规则**: `reportUnknownVariableType`
- **位置**: 第 839 行, 第 19 列
- **错误信息**: 返回类型未知

#### 120. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:846

- **规则**: `reportIndexIssue`
- **位置**: 第 846 行, 第 47 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 121. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:862

- **规则**: `reportMissingImports`
- **位置**: 第 862 行, 第 17 列
- **错误信息**: 无法解析导入 "test_automation_agent"

#### 122. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:862

- **规则**: `reportUnknownVariableType`
- **位置**: 第 862 行, 第 46 列
- **错误信息**: "TestAutomationAgent" 类型未知

#### 123. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:864

- **规则**: `reportUnknownVariableType`
- **位置**: 第 864 行, 第 12 列
- **错误信息**: "test_agent" 类型未知

#### 124. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:870

- **规则**: `reportUnknownVariableType`
- **位置**: 第 870 行, 第 12 列
- **错误信息**: "test_results" 类型未知

#### 125. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:870

- **规则**: `reportUnknownMemberType`
- **位置**: 第 870 行, 第 33 列
- **错误信息**: "run_test_automation" 类型未知

#### 126. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:876

- **规则**: `reportUnknownVariableType`
- **位置**: 第 876 行, 第 12 列
- **错误信息**: "status" 类型未知

#### 127. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:876

- **规则**: `reportUnknownMemberType`
- **位置**: 第 876 行, 第 21 列
- **错误信息**: "get" 类型未知

#### 128. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:877

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 877 行, 第 59 列
- **错误信息**: 参数类型未知
  实参对应于 "_update_progress" 函数中的 "status" 形参

#### 129. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:877

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 877 行, 第 67 列
- **错误信息**: 参数类型未知
  实参对应于 "_update_progress" 函数中的 "details" 形参

#### 130. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:886

- **规则**: `reportUnknownVariableType`
- **位置**: 第 886 行, 第 19 列
- **错误信息**: 返回类型未知

#### 131. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:914

- **规则**: `reportIndexIssue`
- **位置**: 第 914 行, 第 71 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 132. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:970

- **规则**: `reportIndexIssue`
- **位置**: 第 970 行, 第 40 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 133. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:985

- **规则**: `reportUnknownMemberType`
- **位置**: 第 985 行, 第 33 列
- **错误信息**: "stories" 的类型部分未知
  "stories" 为 "list[Unknown]" 类型

#### 134. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:985

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 985 行, 第 33 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 135. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:123

- **规则**: `reportAssignmentType`
- **位置**: 第 123 行, 第 14 列
- **错误信息**: "Path" 类型不匹配声明的 "str" 类型
  "Path" 与 "str" 不兼容

#### 136. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:128

- **规则**: `reportUnknownMemberType`
- **位置**: 第 128 行, 第 15 列
- **错误信息**: "exists" 类型未知

#### 137. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:128

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 128 行, 第 23 列
- **错误信息**: 无法访问 "str" 类的 "exists" 属性
  属性 "exists" 未知

#### 138. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:132

- **规则**: `reportArgumentType`
- **位置**: 第 132 行, 第 36 列
- **错误信息**: "str" 类型的实参无法赋值给函数 "create_backup" 中 "Path" 类型的形参 "db_path"
  "str" 与 "Path" 不兼容

#### 139. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:194

- **规则**: `reportUnknownMemberType`
- **位置**: 第 194 行, 第 29 列
- **错误信息**: "parent" 类型未知

#### 140. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:194

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 194 行, 第 29 列
- **错误信息**: 参数类型未知
  实参对应于 "__new__" 函数中的 "object" 形参

#### 141. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:194

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 194 行, 第 37 列
- **错误信息**: 无法访问 "str" 类的 "parent" 属性
  属性 "parent" 未知

#### 142. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:194

- **规则**: `reportUnknownMemberType`
- **位置**: 第 194 行, 第 49 列
- **错误信息**: "stem" 类型未知

#### 143. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:194

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 194 行, 第 57 列
- **错误信息**: 无法访问 "str" 类的 "stem" 属性
  属性 "stem" 未知

#### 144. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:198

- **规则**: `reportArgumentType`
- **位置**: 第 198 行, 第 31 列
- **错误信息**: "str" 类型的实参无法赋值给函数 "rollback_migration" 中 "Path" 类型的形参 "db_path"
  "str" 与 "Path" 不兼容

#### 145. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:16

- **规则**: `reportMissingImports`
- **位置**: 第 16 行, 第 9 列
- **错误信息**: 无法解析导入 "qa_tools_integration"

#### 146. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:16

- **规则**: `reportUnknownVariableType`
- **位置**: 第 16 行, 第 37 列
- **错误信息**: "QAAutomationWorkflow" 类型未知

#### 147. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:16

- **规则**: `reportUnknownVariableType`
- **位置**: 第 16 行, 第 59 列
- **错误信息**: "QAStatus" 类型未知

#### 148. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:36

- **规则**: `reportUnknownMemberType`
- **位置**: 第 36 行, 第 34 列
- **错误信息**: "value" 类型未知

#### 149. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:36

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 36 行, 第 50 列
- **错误信息**: 无法访问 "Literal['WAIVED']" 类的 "value" 属性
  属性 "value" 未知

#### 150. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:42

- **规则**: `reportConstantRedefinition`
- **位置**: 第 42 行, 第 4 列
- **错误信息**: 不能重新定义常量 "QA_TOOLS_AVAILABLE"（全大写名称）

#### 151. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:108

- **规则**: `reportUnknownVariableType`
- **位置**: 第 108 行, 第 20 列
- **错误信息**: "tool_results" 的类型部分未知
  "tool_results" 为 "dict[str, str | Unknown]" 类型

#### 152. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:110

- **规则**: `reportUnknownMemberType`
- **位置**: 第 110 行, 第 42 列
- **错误信息**: "value" 类型未知

#### 153. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:110

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 110 行, 第 56 列
- **错误信息**: 无法访问 "Literal['FAIL']" 类的 "value" 属性
  属性 "value" 未知

#### 154. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:114

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 114 行, 第 63 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "_calculate_qa_result" 函数中的 "tool_results" 形参
  参数类型为 "Dict[str, Any] | dict[str, str | Unknown]"

#### 155. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:146

- **规则**: `reportUnknownVariableType`
- **位置**: 第 146 行, 第 12 列
- **错误信息**: "data" 的类型部分未知
  "data" 为 "dict[str, str | list[Unknown] | None]" 类型

#### 156. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:215

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 215 行, 第 44 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 157. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:216

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 216 行, 第 23 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 158. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:216

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 216 行, 第 51 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 159. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:218

- **规则**: `reportUnknownVariableType`
- **位置**: 第 218 行, 第 19 列
- **错误信息**: 返回类型 "dict[str, str | list[Unknown] | None]" 部分未知

#### 160. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:383

- **规则**: `reportUnknownMemberType`
- **位置**: 第 383 行, 第 34 列
- **错误信息**: "value" 类型未知

#### 161. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:383

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 383 行, 第 50 列
- **错误信息**: 无法访问 "Literal['WAIVED']" 类的 "value" 属性
  属性 "value" 未知

#### 162. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:412

- **规则**: `reportUnknownMemberType`
- **位置**: 第 412 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 163. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:415

- **规则**: `reportUnknownMemberType`
- **位置**: 第 415 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 164. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:419

- **规则**: `reportUnknownMemberType`
- **位置**: 第 419 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 165. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:422

- **规则**: `reportUnknownMemberType`
- **位置**: 第 422 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 166. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:425

- **规则**: `reportUnknownMemberType`
- **位置**: 第 425 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 167. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:429

- **规则**: `reportUnknownMemberType`
- **位置**: 第 429 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 168. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:432

- **规则**: `reportUnknownMemberType`
- **位置**: 第 432 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 169. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:441

- **规则**: `reportUnknownMemberType`
- **位置**: 第 441 行, 第 33 列
- **错误信息**: "value" 类型未知

#### 170. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:441

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 441 行, 第 47 列
- **错误信息**: 无法访问 "Literal['FAIL']" 类的 "value" 属性
  属性 "value" 未知

#### 171. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:444

- **规则**: `reportUnknownMemberType`
- **位置**: 第 444 行, 第 51 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 172. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:445

- **规则**: `reportUnknownMemberType`
- **位置**: 第 445 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 173. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:451

- **规则**: `reportUnknownMemberType`
- **位置**: 第 451 行, 第 51 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 174. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:452

- **规则**: `reportUnknownMemberType`
- **位置**: 第 452 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 175. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:454

- **规则**: `reportUnknownMemberType`
- **位置**: 第 454 行, 第 27 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 176. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:457

- **规则**: `reportUnknownMemberType`
- **位置**: 第 457 行, 第 35 列
- **错误信息**: "value" 类型未知

#### 177. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:457

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 457 行, 第 53 列
- **错误信息**: 无法访问 "Literal['CONCERNS']" 类的 "value" 属性
  属性 "value" 未知

#### 178. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:460

- **规则**: `reportUnknownMemberType`
- **位置**: 第 460 行, 第 51 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 179. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:461

- **规则**: `reportUnknownMemberType`
- **位置**: 第 461 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 180. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:466

- **规则**: `reportUnknownMemberType`
- **位置**: 第 466 行, 第 51 列
- **错误信息**: "get" 的类型部分未知
  "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型

#### 181. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:467

- **规则**: `reportUnknownMemberType`
- **位置**: 第 467 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 182. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:472

- **规则**: `reportUnknownVariableType`
- **位置**: 第 472 行, 第 8 列
- **错误信息**: "all_failures" 的类型部分未知
  "all_failures" 为 "list[Unknown]" 类型

#### 183. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:473

- **规则**: `reportUnknownVariableType`
- **位置**: 第 473 行, 第 8 列
- **错误信息**: "all_warnings" 的类型部分未知
  "all_warnings" 为 "list[Unknown]" 类型

#### 184. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:482

- **规则**: `reportUnknownMemberType`
- **位置**: 第 482 行, 第 33 列
- **错误信息**: "value" 类型未知

#### 185. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:482

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 482 行, 第 47 列
- **错误信息**: 无法访问 "Literal['PASS']" 类的 "value" 属性
  属性 "value" 未知

#### 186. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:484

- **规则**: `reportUnknownMemberType`
- **位置**: 第 484 行, 第 35 列
- **错误信息**: "value" 类型未知

#### 187. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:484

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 484 行, 第 53 列
- **错误信息**: 无法访问 "Literal['CONCERNS']" 类的 "value" 属性
  属性 "value" 未知

#### 188. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:486

- **规则**: `reportUnknownMemberType`
- **位置**: 第 486 行, 第 35 列
- **错误信息**: "value" 类型未知

#### 189. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:486

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 486 行, 第 49 列
- **错误信息**: 无法访问 "Literal['FAIL']" 类的 "value" 属性
  属性 "value" 未知

#### 190. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:488

- **规则**: `reportUnknownMemberType`
- **位置**: 第 488 行, 第 35 列
- **错误信息**: "value" 类型未知

#### 191. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:488

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 488 行, 第 51 列
- **错误信息**: 无法访问 "Literal['WAIVED']" 类的 "value" 属性
  属性 "value" 未知

#### 192. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:499

- **规则**: `reportUnknownMemberType`
- **位置**: 第 499 行, 第 49 列
- **错误信息**: "value" 类型未知

#### 193. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:499

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 499 行, 第 63 列
- **错误信息**: 无法访问 "Literal['FAIL']" 类的 "value" 属性
  属性 "value" 未知

#### 194. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:501

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 501 行, 第 21 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 195. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:503

- **规则**: `reportUnknownVariableType`
- **位置**: 第 503 行, 第 8 列
- **错误信息**: "result" 的类型部分未知
  "result" 为 "dict[str, Any | bool | int | list[Unknown] | Dict[str, Any] | dict[str, int | Any | str]]" 类型

#### 196. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:518

- **规则**: `reportUnknownVariableType`
- **位置**: 第 518 行, 第 15 列
- **错误信息**: 返回类型 "dict[str, Any | bool | int | list[Unknown] | Dict[str, Any] | dict[str, int | Any | str]]" 部分未知

#### 197. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:78

- **规则**: `reportUnknownVariableType`
- **位置**: 第 78 行, 第 8 列
- **错误信息**: "result" 的类型部分未知
  "result" 为 "dict[str, QAStatus | str | int | list[Unknown]]" 类型

#### 198. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:97

- **规则**: `reportArgumentType`
- **位置**: 第 97 行, 第 105 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "_parse_basedpyright_output" 中 "int" 类型的形参 "returncode"
  "int | None" 类型与 "int" 类型不兼容
    "None" 与 "int" 不兼容

#### 199. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:115

- **规则**: `reportArgumentType`
- **位置**: 第 115 行, 第 102 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "_parse_basedpyright_output" 中 "int" 类型的形参 "returncode"
  "int | None" 类型与 "int" 类型不兼容
    "None" 与 "int" 不兼容

#### 200. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:139

- **规则**: `reportUnknownVariableType`
- **位置**: 第 139 行, 第 15 列
- **错误信息**: 返回类型 "dict[str, QAStatus | str | int | list[Unknown]]" 部分未知

#### 201. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:164

- **规则**: `reportUnknownParameterType`
- **位置**: 第 164 行, 第 16 列
- **错误信息**: 返回类型未知

#### 202. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:164

- **规则**: `reportUnknownParameterType`
- **位置**: 第 164 行, 第 28 列
- **错误信息**: "data" 参数的类型未知

#### 203. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:164

- **规则**: `reportMissingParameterType`
- **位置**: 第 164 行, 第 28 列
- **错误信息**: "data" 参数缺少类型注解

#### 204. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:166

- **规则**: `reportUnknownMemberType`
- **位置**: 第 166 行, 第 27 列
- **错误信息**: "decode" 类型未知

#### 205. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:166

- **规则**: `reportUnknownVariableType`
- **位置**: 第 166 行, 第 27 列
- **错误信息**: 返回类型未知

#### 206. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:169

- **规则**: `reportUnknownMemberType`
- **位置**: 第 169 行, 第 27 列
- **错误信息**: "decode" 类型未知

#### 207. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:169

- **规则**: `reportUnknownVariableType`
- **位置**: 第 169 行, 第 27 列
- **错误信息**: 返回类型未知

#### 208. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:196

- **规则**: `reportUnusedVariable`
- **位置**: 第 196 行, 第 12 列
- **错误信息**: 变量 "stdout" 未使用

#### 209. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:316

- **规则**: `reportUnknownVariableType`
- **位置**: 第 316 行, 第 8 列
- **错误信息**: "result" 的类型部分未知
  "result" 为 "dict[str, QAStatus | str | int | list[Unknown]]" 类型

#### 210. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:338

- **规则**: `reportUnknownVariableType`
- **位置**: 第 338 行, 第 23 列
- **错误信息**: 返回类型 "dict[str, QAStatus | str | int | list[Unknown]]" 部分未知

#### 211. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:346

- **规则**: `reportArgumentType`
- **位置**: 第 346 行, 第 77 列
- **错误信息**: "int | None" 类型的实参无法赋值给函数 "_parse_test_output" 中 "int" 类型的形参 "returncode"
  "int | None" 类型与 "int" 类型不兼容
    "None" 与 "int" 不兼容

#### 212. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:372

- **规则**: `reportUnknownVariableType`
- **位置**: 第 372 行, 第 15 列
- **错误信息**: 返回类型 "dict[str, QAStatus | str | int | list[Unknown]]" 部分未知

#### 213. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:403

- **规则**: `reportUnknownMemberType`
- **位置**: 第 403 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 214. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:405

- **规则**: `reportUnknownVariableType`
- **位置**: 第 405 行, 第 19 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 215. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:431

- **规则**: `reportUnknownParameterType`
- **位置**: 第 431 行, 第 16 列
- **错误信息**: 返回类型未知

#### 216. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:431

- **规则**: `reportUnknownParameterType`
- **位置**: 第 431 行, 第 28 列
- **错误信息**: "data" 参数的类型未知

#### 217. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:431

- **规则**: `reportMissingParameterType`
- **位置**: 第 431 行, 第 28 列
- **错误信息**: "data" 参数缺少类型注解

#### 218. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:433

- **规则**: `reportUnknownMemberType`
- **位置**: 第 433 行, 第 27 列
- **错误信息**: "decode" 类型未知

#### 219. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:433

- **规则**: `reportUnknownVariableType`
- **位置**: 第 433 行, 第 27 列
- **错误信息**: 返回类型未知

#### 220. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:436

- **规则**: `reportUnknownMemberType`
- **位置**: 第 436 行, 第 27 列
- **错误信息**: "decode" 类型未知

#### 221. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:436

- **规则**: `reportUnknownVariableType`
- **位置**: 第 436 行, 第 27 列
- **错误信息**: 返回类型未知

#### 222. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:589

- **规则**: `reportUnknownVariableType`
- **位置**: 第 589 行, 第 8 列
- **错误信息**: "summary" 的类型部分未知
  "summary" 为 "dict[str, str | dict[str, Any] | list[Unknown]]" 类型

#### 223. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:624

- **规则**: `reportUnknownVariableType`
- **位置**: 第 624 行, 第 15 列
- **错误信息**: 返回类型 "dict[str, str | dict[str, Any] | list[Unknown]]" 部分未知

#### 224. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:78

- **规则**: `reportUnknownVariableType`
- **位置**: 第 78 行, 第 12 列
- **错误信息**: "metadata" 的类型部分未知
  "metadata" 为 "dict[str, str | list[Unknown] | None]" 类型

#### 225. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:107

- **规则**: `reportUnknownVariableType`
- **位置**: 第 107 行, 第 19 列
- **错误信息**: 返回类型 "dict[str, str | list[Unknown] | None]" 部分未知

#### 226. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:128

- **规则**: `reportUnknownMemberType`
- **位置**: 第 128 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 227. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:131

- **规则**: `reportUnknownMemberType`
- **位置**: 第 131 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 228. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:136

- **规则**: `reportUnknownMemberType`
- **位置**: 第 136 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 229. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:138

- **规则**: `reportUnknownMemberType`
- **位置**: 第 138 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 230. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:143

- **规则**: `reportUnknownMemberType`
- **位置**: 第 143 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 231. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:145

- **规则**: `reportUnknownVariableType`
- **位置**: 第 145 行, 第 8 列
- **错误信息**: "result" 的类型部分未知
  "result" 为 "dict[str, bool | list[Unknown]]" 类型

#### 232. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:146

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 146 行, 第 25 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 233. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:156

- **规则**: `reportUnknownVariableType`
- **位置**: 第 156 行, 第 15 列
- **错误信息**: 返回类型 "dict[str, bool | list[Unknown]]" 部分未知

#### 234. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:212

- **规则**: `reportUnknownVariableType`
- **位置**: 第 212 行, 第 12 列
- **错误信息**: "story_data" 的类型部分未知
  "story_data" 为 "dict[str, str | list[Unknown]]" 类型

#### 235. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:222

- **规则**: `reportUnknownVariableType`
- **位置**: 第 222 行, 第 19 列
- **错误信息**: 返回类型 "dict[str, str | list[Unknown]]" 部分未知

#### 236. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:144

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 144 行, 第 19 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 237. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:145

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 145 行, 第 23 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 238. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:146

- **规则**: `reportIndexIssue`
- **位置**: 第 146 行, 第 19 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 239. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:146

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 146 行, 第 34 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 240. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:147

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 147 行, 第 19 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 241. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:148

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 148 行, 第 23 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 242. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:182

- **规则**: `reportUnknownParameterType`
- **位置**: 第 182 行, 第 28 列
- **错误信息**: 返回类型 "Unknown | dict[Unknown, Unknown | dict[Unknown, Unknown] | list[Unknown | dict[Unknown, Unknown] | list[Unknown]]] | list[Unknown | dict[Unknown, Unknown] | list[Unknown]]" 部分未知

#### 243. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:182

- **规则**: `reportUnknownParameterType`
- **位置**: 第 182 行, 第 43 列
- **错误信息**: "obj" 参数的类型未知

#### 244. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:182

- **规则**: `reportMissingParameterType`
- **位置**: 第 182 行, 第 43 列
- **错误信息**: "obj" 参数缺少类型注解

#### 245. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:183

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 183 行, 第 39 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 246. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:184

- **规则**: `reportUnknownMemberType`
- **位置**: 第 184 行, 第 39 列
- **错误信息**: "value" 类型未知

#### 247. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:184

- **规则**: `reportUnknownVariableType`
- **位置**: 第 184 行, 第 39 列
- **错误信息**: 返回类型未知

#### 248. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:186

- **规则**: `reportUnknownVariableType`
- **位置**: 第 186 行, 第 39 列
- **错误信息**: 返回类型 "dict[Unknown, Unknown | dict[Unknown, Unknown] | list[Unknown | dict[Unknown, Unknown] | list[Unknown]]]" 部分未知

#### 249. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:186

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 186 行, 第 58 列
- **错误信息**: 参数类型未知
  实参对应于 "clean_for_json" 函数中的 "obj" 形参

#### 250. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:186

- **规则**: `reportUnknownVariableType`
- **位置**: 第 186 行, 第 65 列
- **错误信息**: "k" 类型未知

#### 251. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:186

- **规则**: `reportUnknownVariableType`
- **位置**: 第 186 行, 第 68 列
- **错误信息**: "v" 类型未知

#### 252. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:188

- **规则**: `reportUnknownVariableType`
- **位置**: 第 188 行, 第 39 列
- **错误信息**: 返回类型 "list[Unknown | dict[Unknown, Unknown | dict[Unknown, Unknown] | list[Unknown]] | list[Unknown]]" 部分未知

#### 253. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:188

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 188 行, 第 55 列
- **错误信息**: 参数类型未知
  实参对应于 "clean_for_json" 函数中的 "obj" 形参

#### 254. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:188

- **规则**: `reportUnknownVariableType`
- **位置**: 第 188 行, 第 62 列
- **错误信息**: "v" 类型未知

#### 255. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:190

- **规则**: `reportUnknownVariableType`
- **位置**: 第 190 行, 第 39 列
- **错误信息**: 返回类型未知

#### 256. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:192

- **规则**: `reportUnknownVariableType`
- **位置**: 第 192 行, 第 24 列
- **错误信息**: "cleaned_qa_result" 的类型部分未知
  "cleaned_qa_result" 为 "Unknown | dict[str, Unknown | dict[str, Unknown] | list[Unknown | dict[str, Unknown] | list[Unknown]]] | list[Unknown | dict[str, Unknown | dict[str, Unknown] | list[Unknown]] | list[Unknown]]" 类型

#### 257. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:242

- **规则**: `reportIndexIssue`
- **位置**: 第 242 行, 第 57 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 258. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:242

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 242 行, 第 72 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 259. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:298

- **规则**: `reportIndexIssue`
- **位置**: 第 298 行, 第 39 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 260. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:298

- **规则**: `reportIndexIssue`
- **位置**: 第 298 行, 第 44 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 261. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:307

- **规则**: `reportUnknownParameterType`
- **位置**: 第 307 行, 第 20 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 262. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:342

- **规则**: `reportUnknownMemberType`
- **位置**: 第 342 行, 第 24 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 263. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:344

- **规则**: `reportUnknownVariableType`
- **位置**: 第 344 行, 第 27 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 264. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:346

- **规则**: `reportUnknownVariableType`
- **位置**: 第 346 行, 第 23 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 265. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:352

- **规则**: `reportIndexIssue`
- **位置**: 第 352 行, 第 58 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 266. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:352

- **规则**: `reportIndexIssue`
- **位置**: 第 352 行, 第 63 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 267. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:364

- **规则**: `reportUnknownParameterType`
- **位置**: 第 364 行, 第 20 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 268. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:400

- **规则**: `reportUnknownMemberType`
- **位置**: 第 400 行, 第 24 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 269. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:402

- **规则**: `reportUnknownVariableType`
- **位置**: 第 402 行, 第 27 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 270. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:404

- **规则**: `reportUnknownVariableType`
- **位置**: 第 404 行, 第 23 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 271. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:443

- **规则**: `reportIndexIssue`
- **位置**: 第 443 行, 第 33 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 272. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:452

- **规则**: `reportUnknownParameterType`
- **位置**: 第 452 行, 第 20 列
- **错误信息**: 返回类型 "dict[Unknown, Unknown]" 部分未知

#### 273. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:469

- **规则**: `reportUnknownVariableType`
- **位置**: 第 469 行, 第 27 列
- **错误信息**: 返回类型 "dict[Unknown, Unknown]" 部分未知

#### 274. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:471

- **规则**: `reportUnknownVariableType`
- **位置**: 第 471 行, 第 23 列
- **错误信息**: 返回类型 "dict[Unknown, Unknown]" 部分未知

#### 275. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:477

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 477 行, 第 41 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 276. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:508

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 508 行, 第 13 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 277. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:563

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 563 行, 第 13 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 278. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:609

- **规则**: `reportIndexIssue`
- **位置**: 第 609 行, 第 63 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 279. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:609

- **规则**: `reportIndexIssue`
- **位置**: 第 609 行, 第 68 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 280. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:621

- **规则**: `reportUnknownParameterType`
- **位置**: 第 621 行, 第 20 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 281. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:638

- **规则**: `reportUnknownMemberType`
- **位置**: 第 638 行, 第 24 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 282. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:649

- **规则**: `reportUnknownVariableType`
- **位置**: 第 649 行, 第 27 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 283. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:651

- **规则**: `reportUnknownVariableType`
- **位置**: 第 651 行, 第 23 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 284. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:657

- **规则**: `reportIndexIssue`
- **位置**: 第 657 行, 第 60 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 285. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:657

- **规则**: `reportIndexIssue`
- **位置**: 第 657 行, 第 65 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 286. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:669

- **规则**: `reportUnknownParameterType`
- **位置**: 第 669 行, 第 20 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 287. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:686

- **规则**: `reportUnknownMemberType`
- **位置**: 第 686 行, 第 24 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 288. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:696

- **规则**: `reportUnknownVariableType`
- **位置**: 第 696 行, 第 27 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 289. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:698

- **规则**: `reportUnknownVariableType`
- **位置**: 第 698 行, 第 23 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 290. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:708

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 708 行, 第 25 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 291. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:763

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 763 行, 第 27 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 292. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:764

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 764 行, 第 24 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 293. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:833

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 833 行, 第 27 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 294. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:834

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 834 行, 第 31 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 295. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:835

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 835 行, 第 34 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 296. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:836

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 836 行, 第 31 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 297. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:837

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 837 行, 第 34 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 298. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:838

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 838 行, 第 33 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 299. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:924

- **规则**: `reportIndexIssue`
- **位置**: 第 924 行, 第 53 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 300. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:924

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 924 行, 第 68 列
- **错误信息**: `Union` 的替代语法需要 Python 3.10 或更高版本

#### 301. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:15

- **规则**: `reportMissingImports`
- **位置**: 第 15 行, 第 5 列
- **错误信息**: 无法解析导入 "autoBMAD.epic_automation.state_manager"

#### 302. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:15

- **规则**: `reportUnknownVariableType`
- **位置**: 第 15 行, 第 51 列
- **错误信息**: "StateManager" 类型未知

#### 303. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:19

- **规则**: `reportMissingImports`
- **位置**: 第 19 行, 第 9 列
- **错误信息**: 无法解析导入 "fixtest_workflow.test_automation_workflow"

#### 304. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:19

- **规则**: `reportUnknownVariableType`
- **位置**: 第 19 行, 第 58 列
- **错误信息**: "run_pytest_execution" 类型未知

#### 305. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:20

- **规则**: `reportMissingImports`
- **位置**: 第 20 行, 第 9 列
- **错误信息**: 无法解析导入 "fixtest_workflow.debugpy_integration"

#### 306. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21

- **规则**: `reportUnknownVariableType`
- **位置**: 第 21 行, 第 8 列
- **错误信息**: "start_debugpy_listener" 类型未知

#### 307. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:22

- **规则**: `reportUnknownVariableType`
- **位置**: 第 22 行, 第 8 列
- **错误信息**: "attach_debugpy" 类型未知

#### 308. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:23

- **规则**: `reportUnknownVariableType`
- **位置**: 第 23 行, 第 8 列
- **错误信息**: "collect_debug_info" 类型未知

#### 309. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:34

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 34 行, 第 33 列
- **错误信息**: "Claude" 是未知的导入符号

#### 310. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:34

- **规则**: `reportUnknownVariableType`
- **位置**: 第 34 行, 第 33 列
- **错误信息**: "Claude" 类型未知

#### 311. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:34

- **规则**: `reportUnusedImport`
- **位置**: 第 34 行, 第 33 列
- **错误信息**: "Claude" 导入项未使用

#### 312. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:44

- **规则**: `reportUnknownParameterType`
- **位置**: 第 44 行, 第 8 列
- **错误信息**: "state_manager" 参数的类型未知

#### 313. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:56

- **规则**: `reportUnknownMemberType`
- **位置**: 第 56 行, 第 8 列
- **错误信息**: "state_manager" 类型未知

#### 314. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:88

- **规则**: `reportUnknownVariableType`
- **位置**: 第 88 行, 第 8 列
- **错误信息**: "results" 的类型部分未知
  "results" 为 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 类型

#### 315. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:105

- **规则**: `reportUnknownMemberType`
- **位置**: 第 105 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "Unknown | ((object: Unknown, /) -> None)" 类型

#### 316. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:105

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 105 行, 第 30 列
- **错误信息**: 无法访问 "str" 类的 "append" 属性
  属性 "append" 未知

#### 317. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:105

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 105 行, 第 30 列
- **错误信息**: 无法访问 "int" 类的 "append" 属性
  属性 "append" 未知

#### 318. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:105

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 105 行, 第 30 列
- **错误信息**: 无法访问 "dict[Unknown, Unknown]" 类的 "append" 属性
  属性 "append" 未知

#### 319. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:106

- **规则**: `reportUnknownVariableType`
- **位置**: 第 106 行, 第 19 列
- **错误信息**: 返回类型 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 部分未知

#### 320. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:123

- **规则**: `reportUnknownVariableType`
- **位置**: 第 123 行, 第 19 列
- **错误信息**: 返回类型 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 部分未知

#### 321. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:128

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 128 行, 第 58 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "_run_initial_tests" 函数中的 "results" 形参
  参数类型为 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]"

#### 322. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:174

- **规则**: `reportUnknownMemberType`
- **位置**: 第 174 行, 第 26 列
- **错误信息**: "state_manager" 类型未知

#### 323. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:174

- **规则**: `reportUnknownMemberType`
- **位置**: 第 174 行, 第 26 列
- **错误信息**: "add_test_phase_record" 类型未知

#### 324. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:282

- **规则**: `reportOptionalCall`
- **位置**: 第 282 行, 第 18 列
- **错误信息**: `None` 不支持调用

#### 325. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:285

- **规则**: `reportUnknownVariableType`
- **位置**: 第 285 行, 第 12 列
- **错误信息**: "attach_success" 类型未知

#### 326. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:285

- **规则**: `reportOptionalCall`
- **位置**: 第 285 行, 第 35 列
- **错误信息**: `None` 不支持调用

#### 327. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:293

- **规则**: `reportUnknownVariableType`
- **位置**: 第 293 行, 第 24 列
- **错误信息**: "debug_info" 类型未知

#### 328. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:293

- **规则**: `reportOptionalCall`
- **位置**: 第 293 行, 第 37 列
- **错误信息**: `None` 不支持调用

#### 329. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:296

- **规则**: `reportUnknownMemberType`
- **位置**: 第 296 行, 第 30 列
- **错误信息**: "state_manager" 类型未知

#### 330. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:296

- **规则**: `reportUnknownMemberType`
- **位置**: 第 296 行, 第 30 列
- **错误信息**: "add_test_phase_record" 类型未知

#### 331. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:335

- **规则**: `reportUnusedVariable`
- **位置**: 第 335 行, 第 16 列
- **错误信息**: 变量 "stdout" 未使用

#### 332. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:335

- **规则**: `reportUnusedVariable`
- **位置**: 第 335 行, 第 24 列
- **错误信息**: 变量 "stderr" 未使用

#### 333. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:362

- **规则**: `reportUnknownVariableType`
- **位置**: 第 362 行, 第 15 列
- **错误信息**: 返回类型未知

#### 334. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:385

- **规则**: `reportUnknownMemberType`
- **位置**: 第 385 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 335. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:396

- **规则**: `reportUnknownVariableType`
- **位置**: 第 396 行, 第 19 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

#### 336. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:413

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 413 行, 第 45 列
- **错误信息**: "Claude" 是未知的导入符号

#### 337. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:413

- **规则**: `reportUnknownVariableType`
- **位置**: 第 413 行, 第 45 列
- **错误信息**: "Claude" 类型未知

#### 338. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:431

- **规则**: `reportUnknownVariableType`
- **位置**: 第 431 行, 第 12 列
- **错误信息**: "claude" 类型未知

#### 339. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:444

- **规则**: `reportUnknownMemberType`
- **位置**: 第 444 行, 第 16 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 340. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:452

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 452 行, 第 42 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "join" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

#### 341. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:460

- **规则**: `reportUnknownVariableType`
- **位置**: 第 460 行, 第 12 列
- **错误信息**: "response" 类型未知

#### 342. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:462

- **规则**: `reportUnknownMemberType`
- **位置**: 第 462 行, 第 35 列
- **错误信息**: "content" 类型未知

#### 343. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:467

- **规则**: `reportUnknownVariableType`
- **位置**: 第 467 行, 第 12 列
- **错误信息**: "response_text" 的类型部分未知
  "response_text" 为 "Unknown | str" 类型

#### 344. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:467

- **规则**: `reportUnknownMemberType`
- **位置**: 第 467 行, 第 28 列
- **错误信息**: "content" 的类型部分未知
  "content" 为 "list[Unknown]" 类型

#### 345. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:467

- **规则**: `reportUnknownMemberType`
- **位置**: 第 467 行, 第 28 列
- **错误信息**: "text" 类型未知

#### 346. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:467

- **规则**: `reportUnknownMemberType`
- **位置**: 第 467 行, 第 67 列
- **错误信息**: "content" 类型未知

#### 347. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:467

- **规则**: `reportUnknownMemberType`
- **位置**: 第 467 行, 第 100 列
- **错误信息**: "content" 类型未知

#### 348. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:467

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 467 行, 第 100 列
- **错误信息**: 参数类型未知
  实参对应于 "__new__" 函数中的 "object" 形参

#### 349. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:473

- **规则**: `reportUnknownVariableType`
- **位置**: 第 473 行, 第 12 列
- **错误信息**: "lines" 的类型部分未知
  "lines" 为 "list[str] | Unknown" 类型

#### 350. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:473

- **规则**: `reportUnknownMemberType`
- **位置**: 第 473 行, 第 20 列
- **错误信息**: "split" 的类型部分未知
  "split" 为 "Unknown | ((sep: str | None = None, maxsplit: SupportsIndex = -1) -> list[str])" 类型

#### 351. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:475

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 475 行, 第 26 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[str] | Unknown"

#### 352. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:476

- **规则**: `reportUnknownVariableType`
- **位置**: 第 476 行, 第 16 列
- **错误信息**: "line" 的类型部分未知
  "line" 为 "str | Unknown" 类型

#### 353. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:476

- **规则**: `reportUnknownMemberType`
- **位置**: 第 476 行, 第 23 列
- **错误信息**: "strip" 的类型部分未知
  "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型

#### 354. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:477

- **规则**: `reportUnknownMemberType`
- **位置**: 第 477 行, 第 19 列
- **错误信息**: "startswith" 的类型部分未知
  "startswith" 为 "((prefix: str | tuple[str, ...], start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> bool) | Unknown" 类型

#### 355. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:479

- **规则**: `reportUnknownVariableType`
- **位置**: 第 479 行, 第 20 列
- **错误信息**: "file_path" 的类型部分未知
  "file_path" 为 "str | Unknown" 类型

#### 356. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:479

- **规则**: `reportUnknownMemberType`
- **位置**: 第 479 行, 第 32 列
- **错误信息**: "replace" 的类型部分未知
  "replace" 为 "((old: str, new: str, count: SupportsIndex = -1, /) -> str) | Unknown" 类型

#### 357. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:479

- **规则**: `reportUnknownMemberType`
- **位置**: 第 479 行, 第 32 列
- **错误信息**: "strip" 的类型部分未知
  "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型

#### 358. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:483

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 483 行, 第 34 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[str] | Unknown"

#### 359. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:486

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 486 行, 第 32 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[str] | Unknown"

#### 360. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:493

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 493 行, 第 34 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[str] | Unknown"

#### 361. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:493

- **规则**: `reportUnknownMemberType`
- **位置**: 第 493 行, 第 49 列
- **错误信息**: "strip" 的类型部分未知
  "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型

#### 362. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:493

- **规则**: `reportUnknownMemberType`
- **位置**: 第 493 行, 第 49 列
- **错误信息**: "startswith" 的类型部分未知
  "startswith" 为 "((prefix: str | tuple[str, ...], start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> bool) | Unknown" 类型

#### 363. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:494

- **规则**: `reportUnknownMemberType`
- **位置**: 第 494 行, 第 24 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 364. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:499

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 499 行, 第 42 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "exists" 函数中的 "path" 形参
  参数类型为 "str | Unknown"

#### 365. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:500

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 500 行, 第 33 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "__new__" 函数中的 "args" 形参
  参数类型为 "str | Unknown"

#### 366. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:500

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 500 行, 第 65 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "join" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

#### 367. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:528

- **规则**: `reportUnknownVariableType`
- **位置**: 第 528 行, 第 12 列
- **错误信息**: "debug_info" 类型未知

#### 368. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:528

- **规则**: `reportOptionalCall`
- **位置**: 第 528 行, 第 25 列
- **错误信息**: `None` 不支持调用

#### 369. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:530

- **规则**: `reportUnknownMemberType`
- **位置**: 第 530 行, 第 18 列
- **错误信息**: "state_manager" 类型未知

#### 370. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:530

- **规则**: `reportUnknownMemberType`
- **位置**: 第 530 行, 第 18 列
- **错误信息**: "add_test_phase_record" 类型未知

#### 371. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:538

- **规则**: `reportUnknownVariableType`
- **位置**: 第 538 行, 第 19 列
- **错误信息**: 返回类型未知

#### 372. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:48

- **规则**: `reportUnknownVariableType`
- **位置**: 第 48 行, 第 8 列
- **错误信息**: "workflow" 类型未知

#### 373. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:57

- **规则**: `reportUnknownVariableType`
- **位置**: 第 57 行, 第 8 列
- **错误信息**: "bp_available" 类型未知

#### 374. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:57

- **规则**: `reportUnknownMemberType`
- **位置**: 第 57 行, 第 23 列
- **错误信息**: "basedpyright_runner" 类型未知

#### 375. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:57

- **规则**: `reportUnknownMemberType`
- **位置**: 第 57 行, 第 23 列
- **错误信息**: "available" 类型未知

#### 376. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:58

- **规则**: `reportUnknownVariableType`
- **位置**: 第 58 行, 第 8 列
- **错误信息**: "ft_available" 类型未知

#### 377. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:58

- **规则**: `reportUnknownMemberType`
- **位置**: 第 58 行, 第 23 列
- **错误信息**: "fixtest_runner" 类型未知

#### 378. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:58

- **规则**: `reportUnknownMemberType`
- **位置**: 第 58 行, 第 23 列
- **错误信息**: "available" 类型未知

#### 379. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:82

- **规则**: `reportUnknownVariableType`
- **位置**: 第 82 行, 第 12 列
- **错误信息**: "driver" 类型未知

#### 380. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:83

- **规则**: `reportUnknownVariableType`
- **位置**: 第 83 行, 第 12 列
- **错误信息**: "stories" 类型未知

#### 381. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:83

- **规则**: `reportUnknownMemberType`
- **位置**: 第 83 行, 第 22 列
- **错误信息**: "parse_epic" 类型未知

#### 382. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:85

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 85 行, 第 41 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 383. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:86

- **规则**: `reportUnknownVariableType`
- **位置**: 第 86 行, 第 16 列
- **错误信息**: "story" 类型未知

#### 384. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:87

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 87 行, 第 61 列
- **错误信息**: 参数类型未知
  实参对应于 "__new__" 函数中的 "args" 形参

#### 385. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:109

- **规则**: `reportUnknownVariableType`
- **位置**: 第 109 行, 第 12 列
- **错误信息**: "agent" 类型未知

#### 386. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:133

- **规则**: `reportUnknownVariableType`
- **位置**: 第 133 行, 第 12 列
- **错误信息**: "result" 类型未知

#### 387. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:133

- **规则**: `reportUnknownMemberType`
- **位置**: 第 133 行, 第 27 列
- **错误信息**: "execute" 类型未知

#### 388. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:139

- **规则**: `reportUnknownMemberType`
- **位置**: 第 139 行, 第 34 列
- **错误信息**: "get" 类型未知

#### 389. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:140

- **规则**: `reportUnknownMemberType`
- **位置**: 第 140 行, 第 35 列
- **错误信息**: "get" 类型未知

#### 390. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:141

- **规则**: `reportUnknownMemberType`
- **位置**: 第 141 行, 第 41 列
- **错误信息**: "get" 类型未知

#### 391. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:29

- **规则**: `reportUnusedImport`
- **位置**: 第 29 行, 第 15 列
- **错误信息**: "argparse" 导入项未使用

#### 392. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:46

- **规则**: `reportUnusedVariable`
- **位置**: 第 46 行, 第 8 列
- **错误信息**: 变量 "test_args" 未使用

#### 393. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:50

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 50 行, 第 24 列
- **错误信息**: 参数类型未知
  实参对应于 "callable" 函数中的 "obj" 形参

#### 394. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:66

- **规则**: `reportUnknownVariableType`
- **位置**: 第 66 行, 第 8 列
- **错误信息**: "driver" 类型未知

#### 395. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:74

- **规则**: `reportUnknownMemberType`
- **位置**: 第 74 行, 第 15 列
- **错误信息**: "epic_path" 类型未知

#### 396. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:75

- **规则**: `reportUnknownMemberType`
- **位置**: 第 75 行, 第 15 列
- **错误信息**: "max_iterations" 类型未知

#### 397. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:76

- **规则**: `reportUnknownMemberType`
- **位置**: 第 76 行, 第 15 列
- **错误信息**: "retry_failed" 类型未知

#### 398. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:77

- **规则**: `reportUnknownMemberType`
- **位置**: 第 77 行, 第 15 列
- **错误信息**: "verbose" 类型未知

#### 399. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:78

- **规则**: `reportUnknownMemberType`
- **位置**: 第 78 行, 第 15 列
- **错误信息**: "concurrent" 类型未知

#### 400. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:173

- **规则**: `reportUnknownMemberType`
- **位置**: 第 173 行, 第 8 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 401. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:204

- **规则**: `reportUnknownMemberType`
- **位置**: 第 204 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 402. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:235

- **规则**: `reportUnknownVariableType`
- **位置**: 第 235 行, 第 12 列
- **错误信息**: "driver" 类型未知

#### 403. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:244

- **规则**: `reportUnknownMemberType`
- **位置**: 第 244 行, 第 19 列
- **错误信息**: "max_iterations" 类型未知

#### 404. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:275

- **规则**: `reportUnknownMemberType`
- **位置**: 第 275 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 405. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:278

- **规则**: `reportUnknownMemberType`
- **位置**: 第 278 行, 第 12 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 406. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:285

- **规则**: `reportUnknownVariableType`
- **位置**: 第 285 行, 第 23 列
- **错误信息**: "_" 类型未知

#### 407. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:285

- **规则**: `reportUnknownVariableType`
- **位置**: 第 285 行, 第 26 列
- **错误信息**: "result" 类型未知

#### 408. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:286

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 286 行, 第 16 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 409. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:288

- **规则**: `reportUnknownVariableType`
- **位置**: 第 288 行, 第 8 列
- **错误信息**: "test_name" 类型未知

#### 410. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:288

- **规则**: `reportUnknownVariableType`
- **位置**: 第 288 行, 第 19 列
- **错误信息**: "result" 类型未知

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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:19:39 - error: "run_basedpyright_check" 是未知的导入符号 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:19:39 - error: "run_basedpyright_check" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:20:39 - error: "run_ruff_check" 是未知的导入符号 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:20:39 - error: "run_ruff_check" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:28:34 - error: "Claude" 是未知的导入符号 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:28:34 - error: "Claude" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:28:34 - error: "Claude" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:76:9 - error: "results" 的类型部分未知
    "results" 为 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:92:13 - error: "append" 的类型部分未知
    "append" 为 "Unknown | ((object: Unknown, /) -> None)" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:92:31 - error: 无法访问 "str" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:92:31 - error: 无法访问 "int" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:92:31 - error: 无法访问 "dict[Unknown, Unknown]" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:93:20 - error: 返回类型 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:102:20 - error: 返回类型 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:129:24 - error: 返回类型 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:150:30 - error: "total_errors" 可能未绑定 (reportPossiblyUnboundVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:154:16 - error: 返回类型 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:169:13 - error: "result" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:169:28 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:174:17 - error: "file_errors" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:174:31 - error: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:174:31 - error: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:175:35 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:177:39 - error: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:187:20 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:211:13 - error: "result" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:211:28 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:216:17 - error: "file_errors" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:216:31 - error: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:216:31 - error: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:217:35 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:219:39 - error: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:230:20 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:256:46 - error: "Claude" 是未知的导入符号 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:256:46 - error: "Claude" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:274:13 - error: "claude" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:277:13 - error: 变量 "fixed_files" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:285:17 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:292:17 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:299:46 - error: 部分参数的类型未知
    实参对应于 "_create_fix_prompt" 函数中的 "errors" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:302:13 - error: "response" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:302:30 - error: "messages" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:302:30 - error: "create" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:315:16 - error: "content" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\code_quality_agent.py:316:54 - error: "content" 类型未知 (reportUnknownMemberType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:151:13 - error: "requirements" 的类型部分未知
    "requirements" 为 "dict[str, str | list[Unknown] | dict[Unknown, Unknown]]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:171:25 - error: "acceptance_criteria" 的类型部分未知
    "acceptance_criteria" 为 "str | list[Unknown] | dict[Unknown, Unknown]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:173:25 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:181:25 - error: "tasks" 的类型部分未知
    "tasks" 为 "str | list[Unknown] | dict[Unknown, Unknown]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:183:25 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:189:21 - error: "subtasks" 的类型部分未知
    "subtasks" 为 "str | list[Unknown] | dict[Unknown, Unknown]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:191:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:196:17 - error: "dev_notes" 的类型部分未知
    "dev_notes" 为 "str | list[Unknown] | dict[Unknown, Unknown]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:203:17 - error: "testing" 的类型部分未知
    "testing" 为 "str | list[Unknown] | dict[Unknown, Unknown]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:207:56 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "str | list[Unknown] | dict[Unknown, Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:207:103 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "str | list[Unknown] | dict[Unknown, Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:207:139 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "str | list[Unknown] | dict[Unknown, Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:208:20 - error: 返回类型 "dict[str, str | list[Unknown] | dict[Unknown, Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:220:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:223:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:227:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:230:26 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:31:14 - error: "list" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:42:20 - error: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:142:29 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:142:34 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:211:25 - error: "story_file" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:212:25 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:214:41 - error: "resolve" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:214:41 - error: 参数类型未知
    实参对应于 "__new__" 函数中的 "object" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:215:37 - error: "name" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:217:25 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:225:29 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:230:29 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:242:52 - error: 部分参数的类型未知
    实参对应于 "__init__" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:247:13 - error: "sort" 的类型部分未知
    "sort" 为 "Overload[(*, key: None = None, reverse: bool = False) -> None, (*, key: (Unknown) -> (SupportsDunderLT[Any] | SupportsDunderGT[Any]), reverse: bool = False) -> None]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:247:37 - error: "x" 参数的类型未知 (reportUnknownLambdaType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:247:40 - error: 该 `lambda` 的返回类型未知 (reportUnknownLambdaType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:250:55 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:252:20 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:260:61 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:281:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:291:17 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:295:9 - error: "seen" 的类型部分未知
    "seen" 为 "set[Unknown]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:297:13 - error: "story_id" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:299:13 - error: "key" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:299:19 - error: "split" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:299:19 - error: "strip" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:299:19 - error: "zfill" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:301:17 - error: "add" 的类型部分未知
    "add" 为 "(element: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:301:26 - error: 参数类型未知
    实参对应于 "add" 函数中的 "element" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:302:17 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:302:41 - error: 参数类型未知
    实参对应于 "append" 函数中的 "object" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:304:39 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:306:16 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:436:89 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:557:13 - error: "guidance" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:557:24 - error: "task_guidance" 的类型部分未知
    "task_guidance" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:557:24 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:610:13 - error: "guidance" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:610:24 - error: "task_guidance" 的类型部分未知
    "task_guidance" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:610:24 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:656:13 - error: "guidance" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:656:24 - error: "task_guidance" 的类型部分未知
    "task_guidance" 为 "dict[Unknown, Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:656:24 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:699:42 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:764:54 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:764:59 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:799:46 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:815:18 - error: 无法解析导入 "code_quality_agent" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:815:44 - error: "CodeQualityAgent" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:817:13 - error: "quality_agent" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:823:13 - error: "quality_results" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:823:37 - error: "run_quality_gates" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:829:13 - error: "status" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:829:22 - error: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:830:58 - error: 参数类型未知
    实参对应于 "_update_progress" 函数中的 "status" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:830:66 - error: 参数类型未知
    实参对应于 "_update_progress" 函数中的 "details" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:839:20 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:846:48 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:862:18 - error: 无法解析导入 "test_automation_agent" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:862:47 - error: "TestAutomationAgent" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:864:13 - error: "test_agent" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:870:13 - error: "test_results" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:870:34 - error: "run_test_automation" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:876:13 - error: "status" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:876:22 - error: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:877:60 - error: 参数类型未知
    实参对应于 "_update_progress" 函数中的 "status" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:877:68 - error: 参数类型未知
    实参对应于 "_update_progress" 函数中的 "details" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:886:20 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:914:72 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:970:41 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:985:34 - error: "stories" 的类型部分未知
    "stories" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:985:34 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:123:15 - error: "Path" 类型不匹配声明的 "str" 类型
    "Path" 与 "str" 不兼容 (reportAssignmentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:128:16 - error: "exists" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:128:24 - error: 无法访问 "str" 类的 "exists" 属性
    属性 "exists" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:132:37 - error: "str" 类型的实参无法赋值给函数 "create_backup" 中 "Path" 类型的形参 "db_path"
    "str" 与 "Path" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:194:30 - error: "parent" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:194:30 - error: 参数类型未知
    实参对应于 "__new__" 函数中的 "object" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:194:38 - error: 无法访问 "str" 类的 "parent" 属性
    属性 "parent" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:194:50 - error: "stem" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:194:58 - error: 无法访问 "str" 类的 "stem" 属性
    属性 "stem" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\migrations\migration_001_add_quality_gates.py:198:32 - error: "str" 类型的实参无法赋值给函数 "rollback_migration" 中 "Path" 类型的形参 "db_path"
    "str" 与 "Path" 不兼容 (reportArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:16:10 - error: 无法解析导入 "qa_tools_integration" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:16:38 - error: "QAAutomationWorkflow" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:16:60 - error: "QAStatus" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:36:35 - error: "value" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:36:51 - error: 无法访问 "Literal['WAIVED']" 类的 "value" 属性
    属性 "value" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:42:5 - error: 不能重新定义常量 "QA_TOOLS_AVAILABLE"（全大写名称） (reportConstantRedefinition)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:108:21 - error: "tool_results" 的类型部分未知
    "tool_results" 为 "dict[str, str | Unknown]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:110:43 - error: "value" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:110:57 - error: 无法访问 "Literal['FAIL']" 类的 "value" 属性
    属性 "value" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:114:64 - error: 部分参数的类型未知
    实参对应于 "_calculate_qa_result" 函数中的 "tool_results" 形参
    参数类型为 "Dict[str, Any] | dict[str, str | Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:146:13 - error: "data" 的类型部分未知
    "data" 为 "dict[str, str | list[Unknown] | None]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:215:45 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:216:24 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:216:52 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:218:20 - error: 返回类型 "dict[str, str | list[Unknown] | None]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:383:35 - error: "value" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:383:51 - error: 无法访问 "Literal['WAIVED']" 类的 "value" 属性
    属性 "value" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:412:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:415:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:419:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:422:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:425:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:429:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:432:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:441:34 - error: "value" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:441:48 - error: 无法访问 "Literal['FAIL']" 类的 "value" 属性
    属性 "value" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:444:52 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:445:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:451:52 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:452:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:454:28 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:457:36 - error: "value" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:457:54 - error: 无法访问 "Literal['CONCERNS']" 类的 "value" 属性
    属性 "value" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:460:52 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:461:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:466:52 - error: "get" 的类型部分未知
    "get" 为 "Overload[(key: Unknown, default: None = None, /) -> (Unknown | None), (key: Unknown, default: Unknown, /) -> Unknown, (key: Unknown, default: _T@get, /) -> (Unknown | _T@get)]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:467:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:472:9 - error: "all_failures" 的类型部分未知
    "all_failures" 为 "list[Unknown]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:473:9 - error: "all_warnings" 的类型部分未知
    "all_warnings" 为 "list[Unknown]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:482:34 - error: "value" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:482:48 - error: 无法访问 "Literal['PASS']" 类的 "value" 属性
    属性 "value" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:484:36 - error: "value" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:484:54 - error: 无法访问 "Literal['CONCERNS']" 类的 "value" 属性
    属性 "value" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:486:36 - error: "value" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:486:50 - error: 无法访问 "Literal['FAIL']" 类的 "value" 属性
    属性 "value" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:488:36 - error: "value" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:488:52 - error: 无法访问 "Literal['WAIVED']" 类的 "value" 属性
    属性 "value" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:499:50 - error: "value" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:499:64 - error: 无法访问 "Literal['FAIL']" 类的 "value" 属性
    属性 "value" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:501:22 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:503:9 - error: "result" 的类型部分未知
    "result" 为 "dict[str, Any | bool | int | list[Unknown] | Dict[str, Any] | dict[str, int | Any | str]]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:518:16 - error: 返回类型 "dict[str, Any | bool | int | list[Unknown] | Dict[str, Any] | dict[str, int | Any | str]]" 部分未知 (reportUnknownVariableType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:78:9 - error: "result" 的类型部分未知
    "result" 为 "dict[str, QAStatus | str | int | list[Unknown]]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:97:106 - error: "int | None" 类型的实参无法赋值给函数 "_parse_basedpyright_output" 中 "int" 类型的形参 "returncode"
    "int | None" 类型与 "int" 类型不兼容
      "None" 与 "int" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:115:103 - error: "int | None" 类型的实参无法赋值给函数 "_parse_basedpyright_output" 中 "int" 类型的形参 "returncode"
    "int | None" 类型与 "int" 类型不兼容
      "None" 与 "int" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:139:16 - error: 返回类型 "dict[str, QAStatus | str | int | list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:164:17 - error: 返回类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:164:29 - error: "data" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:164:29 - error: "data" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:166:28 - error: "decode" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:166:28 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:169:28 - error: "decode" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:169:28 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:196:13 - error: 变量 "stdout" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:316:9 - error: "result" 的类型部分未知
    "result" 为 "dict[str, QAStatus | str | int | list[Unknown]]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:338:24 - error: 返回类型 "dict[str, QAStatus | str | int | list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:346:78 - error: "int | None" 类型的实参无法赋值给函数 "_parse_test_output" 中 "int" 类型的形参 "returncode"
    "int | None" 类型与 "int" 类型不兼容
      "None" 与 "int" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:372:16 - error: 返回类型 "dict[str, QAStatus | str | int | list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:403:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:405:20 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:431:17 - error: 返回类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:431:29 - error: "data" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:431:29 - error: "data" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:433:28 - error: "decode" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:433:28 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:436:28 - error: "decode" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:436:28 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:589:9 - error: "summary" 的类型部分未知
    "summary" 为 "dict[str, str | dict[str, Any] | list[Unknown]]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:624:16 - error: 返回类型 "dict[str, str | dict[str, Any] | list[Unknown]]" 部分未知 (reportUnknownVariableType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:78:13 - error: "metadata" 的类型部分未知
    "metadata" 为 "dict[str, str | list[Unknown] | None]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:107:20 - error: 返回类型 "dict[str, str | list[Unknown] | None]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:128:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:131:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:136:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:138:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:143:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:145:9 - error: "result" 的类型部分未知
    "result" 为 "dict[str, bool | list[Unknown]]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:146:26 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:156:16 - error: 返回类型 "dict[str, bool | list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:212:13 - error: "story_data" 的类型部分未知
    "story_data" 为 "dict[str, str | list[Unknown]]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:222:20 - error: 返回类型 "dict[str, str | list[Unknown]]" 部分未知 (reportUnknownVariableType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:144:20 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:145:24 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:146:20 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:146:35 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:147:20 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:148:24 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:182:29 - error: 返回类型 "Unknown | dict[Unknown, Unknown | dict[Unknown, Unknown] | list[Unknown | dict[Unknown, Unknown] | list[Unknown]]] | list[Unknown | dict[Unknown, Unknown] | list[Unknown]]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:182:44 - error: "obj" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:182:44 - error: "obj" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:183:40 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:184:40 - error: "value" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:184:40 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:186:40 - error: 返回类型 "dict[Unknown, Unknown | dict[Unknown, Unknown] | list[Unknown | dict[Unknown, Unknown] | list[Unknown]]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:186:59 - error: 参数类型未知
    实参对应于 "clean_for_json" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:186:66 - error: "k" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:186:69 - error: "v" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:188:40 - error: 返回类型 "list[Unknown | dict[Unknown, Unknown | dict[Unknown, Unknown] | list[Unknown]] | list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:188:56 - error: 参数类型未知
    实参对应于 "clean_for_json" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:188:63 - error: "v" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:190:40 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:192:25 - error: "cleaned_qa_result" 的类型部分未知
    "cleaned_qa_result" 为 "Unknown | dict[str, Unknown | dict[str, Unknown] | list[Unknown | dict[str, Unknown] | list[Unknown]]] | list[Unknown | dict[str, Unknown | dict[str, Unknown] | list[Unknown]] | list[Unknown]]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:242:58 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:242:73 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:298:40 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:298:45 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:307:21 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:342:25 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:344:28 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:346:24 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:352:59 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:352:64 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:364:21 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:400:25 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:402:28 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:404:24 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:443:34 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:452:21 - error: 返回类型 "dict[Unknown, Unknown]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:469:28 - error: 返回类型 "dict[Unknown, Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:471:24 - error: 返回类型 "dict[Unknown, Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:477:42 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:508:14 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:563:14 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:609:64 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:609:69 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:621:21 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:638:25 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:649:28 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:651:24 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:657:61 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:657:66 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:669:21 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:686:25 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:696:28 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:698:24 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:708:26 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:763:28 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:764:25 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:833:28 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:834:32 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:835:35 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:836:32 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:837:35 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:838:34 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:924:54 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:924:69 - error: `Union` 的替代语法需要 Python 3.10 或更高版本 (reportGeneralTypeIssues)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:15:6 - error: 无法解析导入 "autoBMAD.epic_automation.state_manager" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:15:52 - error: "StateManager" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:19:10 - error: 无法解析导入 "fixtest_workflow.test_automation_workflow" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:19:59 - error: "run_pytest_execution" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:20:10 - error: 无法解析导入 "fixtest_workflow.debugpy_integration" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21:9 - error: "start_debugpy_listener" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:22:9 - error: "attach_debugpy" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:23:9 - error: "collect_debug_info" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:34:34 - error: "Claude" 是未知的导入符号 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:34:34 - error: "Claude" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:34:34 - error: "Claude" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:44:9 - error: "state_manager" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:56:9 - error: "state_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:88:9 - error: "results" 的类型部分未知
    "results" 为 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:105:13 - error: "append" 的类型部分未知
    "append" 为 "Unknown | ((object: Unknown, /) -> None)" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:105:31 - error: 无法访问 "str" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:105:31 - error: 无法访问 "int" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:105:31 - error: 无法访问 "dict[Unknown, Unknown]" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:106:20 - error: 返回类型 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:123:20 - error: 返回类型 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:128:59 - error: 部分参数的类型未知
    实参对应于 "_run_initial_tests" 函数中的 "results" 形参
    参数类型为 "dict[str, str | int | dict[Unknown, Unknown] | list[Unknown]]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:174:27 - error: "state_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:174:27 - error: "add_test_phase_record" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:282:19 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:285:13 - error: "attach_success" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:285:36 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:293:25 - error: "debug_info" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:293:38 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:296:31 - error: "state_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:296:31 - error: "add_test_phase_record" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:335:17 - error: 变量 "stdout" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:335:25 - error: 变量 "stderr" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:362:16 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:385:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:396:20 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:413:46 - error: "Claude" 是未知的导入符号 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:413:46 - error: "Claude" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:431:13 - error: "claude" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:444:17 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:452:43 - error: 部分参数的类型未知
    实参对应于 "join" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:460:13 - error: "response" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:462:36 - error: "content" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:467:13 - error: "response_text" 的类型部分未知
    "response_text" 为 "Unknown | str" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:467:29 - error: "content" 的类型部分未知
    "content" 为 "list[Unknown]" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:467:29 - error: "text" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:467:68 - error: "content" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:467:101 - error: "content" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:467:101 - error: 参数类型未知
    实参对应于 "__new__" 函数中的 "object" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:473:13 - error: "lines" 的类型部分未知
    "lines" 为 "list[str] | Unknown" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:473:21 - error: "split" 的类型部分未知
    "split" 为 "Unknown | ((sep: str | None = None, maxsplit: SupportsIndex = -1) -> list[str])" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:475:27 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[str] | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:476:17 - error: "line" 的类型部分未知
    "line" 为 "str | Unknown" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:476:24 - error: "strip" 的类型部分未知
    "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:477:20 - error: "startswith" 的类型部分未知
    "startswith" 为 "((prefix: str | tuple[str, ...], start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> bool) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:479:21 - error: "file_path" 的类型部分未知
    "file_path" 为 "str | Unknown" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:479:33 - error: "replace" 的类型部分未知
    "replace" 为 "((old: str, new: str, count: SupportsIndex = -1, /) -> str) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:479:33 - error: "strip" 的类型部分未知
    "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:483:35 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[str] | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:486:33 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[str] | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:493:35 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[str] | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:493:50 - error: "strip" 的类型部分未知
    "strip" 为 "((chars: str | None = None, /) -> str) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:493:50 - error: "startswith" 的类型部分未知
    "startswith" 为 "((prefix: str | tuple[str, ...], start: SupportsIndex | None = None, end: SupportsIndex | None = None, /) -> bool) | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:494:25 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:499:43 - error: 部分参数的类型未知
    实参对应于 "exists" 函数中的 "path" 形参
    参数类型为 "str | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:500:34 - error: 部分参数的类型未知
    实参对应于 "__new__" 函数中的 "args" 形参
    参数类型为 "str | Unknown" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:500:66 - error: 部分参数的类型未知
    实参对应于 "join" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:528:13 - error: "debug_info" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:528:26 - error: `None` 不支持调用 (reportOptionalCall)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:530:19 - error: "state_manager" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:530:19 - error: "add_test_phase_record" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:538:20 - error: 返回类型未知 (reportUnknownVariableType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:48:9 - error: "workflow" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:57:9 - error: "bp_available" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:57:24 - error: "basedpyright_runner" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:57:24 - error: "available" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:58:9 - error: "ft_available" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:58:24 - error: "fixtest_runner" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:58:24 - error: "available" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:82:13 - error: "driver" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:83:13 - error: "stories" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:83:23 - error: "parse_epic" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:85:42 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:86:17 - error: "story" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:87:62 - error: 参数类型未知
    实参对应于 "__new__" 函数中的 "args" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:109:13 - error: "agent" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:133:13 - error: "result" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:133:28 - error: "execute" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:139:35 - error: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:140:36 - error: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_changes.py:141:42 - error: "get" 类型未知 (reportUnknownMemberType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:29:16 - error: "argparse" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:46:9 - error: 变量 "test_args" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:50:25 - error: 参数类型未知
    实参对应于 "callable" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:66:9 - error: "driver" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:74:16 - error: "epic_path" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:75:16 - error: "max_iterations" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:76:16 - error: "retry_failed" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:77:16 - error: "verbose" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:78:16 - error: "concurrent" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:173:9 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:204:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:235:13 - error: "driver" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:244:20 - error: "max_iterations" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:275:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:278:13 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:285:24 - error: "_" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:285:27 - error: "result" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:286:17 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:288:9 - error: "test_name" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_portability.py:288:20 - error: "result" 类型未知 (reportUnknownVariableType)
410 errors, 0 warnings, 0 notes
```


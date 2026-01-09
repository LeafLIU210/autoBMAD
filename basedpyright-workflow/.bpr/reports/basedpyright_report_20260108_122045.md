# BasedPyright 检查报告
**生成时间**: 2026-01-08 12:20:45
**检查时间**: 2026-01-08T12:20:45.204323
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 15 |
| ❌ 错误 (Error) | 141 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.75 秒 |

## 🔴 错误详情

共发现 **141** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 76 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py`: 29 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py`: 28 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py`: 8 个错误

### 按规则分组

- `reportIndexIssue`: 35 次
- `reportAttributeAccessIssue`: 30 次
- `reportArgumentType`: 18 次
- `reportOptionalMemberAccess`: 13 次
- `reportUnknownArgumentType`: 11 次
- `reportOptionalSubscript`: 8 次
- `reportCallIssue`: 8 次
- `reportUnusedImport`: 5 次
- `reportOperatorIssue`: 5 次
- `reportUnusedVariable`: 4 次
- `reportUnnecessaryIsInstance`: 2 次
- `reportInvalidTypeForm`: 1 次
- `reportUnnecessaryComparison`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:18

- **规则**: `reportUnusedImport`
- **位置**: 第 18 行, 第 32 列
- **错误信息**: "Message" 导入项未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:109

- **规则**: `reportInvalidTypeForm`
- **位置**: 第 109 行, 第 36 列
- **错误信息**: 类型表达式中不允许使用变量

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:111

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 111 行, 第 36 列
- **错误信息**: 参数类型未知
  实参对应于 "getattr" 函数中的 "o" 形参

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:113

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 113 行, 第 40 列
- **错误信息**: 参数类型未知
  实参对应于 "getattr" 函数中的 "o" 形参

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:355

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 355 行, 第 23 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:357

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 357 行, 第 25 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:406

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 406 行, 第 23 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:408

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 408 行, 第 25 列
- **错误信息**: 参数类型未知
  实参对应于 "hasattr" 函数中的 "obj" 形参

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:77

- **规则**: `reportOperatorIssue`
- **位置**: 第 77 行, 第 11 列
- **错误信息**: "str" 与 "bool | float | dict[str, str | dict[str, str | None]] | list[Unknown] | None" 类型不支持 "in" 运算符
  "str" 与 "bool" 类型不支持 "in" 运算符
  "str" 与 "None" 类型不支持 "in" 运算符
  "str" 与 "float" 类型不支持 "in" 运算符

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:78

- **规则**: `reportIndexIssue`
- **位置**: 第 78 行, 第 12 列
- **错误信息**: "bool" 类型上未定义 "__getitem__" 方法

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:78

- **规则**: `reportOptionalSubscript`
- **位置**: 第 78 行, 第 12 列
- **错误信息**: `None` 不支持下标访问

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:78

- **规则**: `reportIndexIssue`
- **位置**: 第 78 行, 第 12 列
- **错误信息**: "float" 类型上未定义 "__getitem__" 方法

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:78

- **规则**: `reportCallIssue`
- **位置**: 第 78 行, 第 12 列
- **错误信息**: "__getitem__" 的重载与提供的参数不匹配

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:78

- **规则**: `reportArgumentType`
- **位置**: 第 78 行, 第 12 列
- **错误信息**: "str" 类型的实参无法赋值给函数 "__getitem__" 中 "slice[Any, Any, Any]" 类型的形参 "s"
  "str" 与 "slice[Any, Any, Any]" 不兼容

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:78

- **规则**: `reportIndexIssue`
- **位置**: 第 78 行, 第 12 列
- **错误信息**: "str" 类型上未定义 "__setitem__" 方法

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:80

- **规则**: `reportIndexIssue`
- **位置**: 第 80 行, 第 16 列
- **错误信息**: "bool" 类型上未定义 "__getitem__" 方法

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:80

- **规则**: `reportOptionalSubscript`
- **位置**: 第 80 行, 第 16 列
- **错误信息**: `None` 不支持下标访问

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:80

- **规则**: `reportIndexIssue`
- **位置**: 第 80 行, 第 16 列
- **错误信息**: "float" 类型上未定义 "__getitem__" 方法

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:80

- **规则**: `reportCallIssue`
- **位置**: 第 80 行, 第 16 列
- **错误信息**: "__getitem__" 的重载与提供的参数不匹配

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:80

- **规则**: `reportArgumentType`
- **位置**: 第 80 行, 第 16 列
- **错误信息**: "str" 类型的实参无法赋值给函数 "__getitem__" 中 "slice[Any, Any, Any]" 类型的形参 "s"
  "str" 与 "slice[Any, Any, Any]" 不兼容

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:80

- **规则**: `reportIndexIssue`
- **位置**: 第 80 行, 第 16 列
- **错误信息**: "str" 类型上未定义 "__setitem__" 方法

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:80

- **规则**: `reportArgumentType`
- **位置**: 第 80 行, 第 16 列
- **错误信息**: "float" 类型的实参无法赋值给函数 "__setitem__" 中 "str | None" 类型的形参 "value"
  "float" 类型与 "str | None" 类型不兼容
    "float" 与 "str" 不兼容
    "float" 与 "None" 不兼容

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:82

- **规则**: `reportIndexIssue`
- **位置**: 第 82 行, 第 16 列
- **错误信息**: "bool" 类型上未定义 "__getitem__" 方法

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:82

- **规则**: `reportOptionalSubscript`
- **位置**: 第 82 行, 第 16 列
- **错误信息**: `None` 不支持下标访问

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:82

- **规则**: `reportIndexIssue`
- **位置**: 第 82 行, 第 16 列
- **错误信息**: "float" 类型上未定义 "__getitem__" 方法

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:82

- **规则**: `reportCallIssue`
- **位置**: 第 82 行, 第 16 列
- **错误信息**: "__getitem__" 的重载与提供的参数不匹配

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:82

- **规则**: `reportArgumentType`
- **位置**: 第 82 行, 第 16 列
- **错误信息**: "str" 类型的实参无法赋值给函数 "__getitem__" 中 "slice[Any, Any, Any]" 类型的形参 "s"
  "str" 与 "slice[Any, Any, Any]" 不兼容

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:82

- **规则**: `reportIndexIssue`
- **位置**: 第 82 行, 第 16 列
- **错误信息**: "str" 类型上未定义 "__setitem__" 方法

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:82

- **规则**: `reportArgumentType`
- **位置**: 第 82 行, 第 16 列
- **错误信息**: "float" 类型的实参无法赋值给函数 "__setitem__" 中 "str | None" 类型的形参 "value"
  "float" 类型与 "str | None" 类型不兼容
    "float" 与 "str" 不兼容
    "float" 与 "None" 不兼容

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:96

- **规则**: `reportIndexIssue`
- **位置**: 第 96 行, 第 8 列
- **错误信息**: "bool" 类型上未定义 "__setitem__" 方法

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:96

- **规则**: `reportOptionalSubscript`
- **位置**: 第 96 行, 第 8 列
- **错误信息**: `None` 不支持下标访问

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:96

- **规则**: `reportIndexIssue`
- **位置**: 第 96 行, 第 8 列
- **错误信息**: "float" 类型上未定义 "__setitem__" 方法

#### 33. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:96

- **规则**: `reportCallIssue`
- **位置**: 第 96 行, 第 8 列
- **错误信息**: "__setitem__" 的重载与提供的参数不匹配

#### 34. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:96

- **规则**: `reportArgumentType`
- **位置**: 第 96 行, 第 8 列
- **错误信息**: "Literal['current_phase']" 类型的实参无法赋值给函数 "__setitem__" 中 "slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['current_phase']" 与 "slice[Any, Any, Any]" 不兼容

#### 35. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:124

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 124 行, 第 39 列
- **错误信息**: 无法访问 "bool" 类的 "append" 属性
  属性 "append" 未知

#### 36. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:124

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 124 行, 第 39 列
- **错误信息**: `None` 没有 "append" 属性

#### 37. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:124

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 124 行, 第 39 列
- **错误信息**: 无法访问 "float" 类的 "append" 属性
  属性 "append" 未知

#### 38. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:124

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 124 行, 第 39 列
- **错误信息**: 无法访问 "dict[str, str | dict[str, str | None]]" 类的 "append" 属性
  属性 "append" 未知

#### 39. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:135

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 135 行, 第 35 列
- **错误信息**: 无法访问 "bool" 类的 "append" 属性
  属性 "append" 未知

#### 40. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:135

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 135 行, 第 35 列
- **错误信息**: `None` 没有 "append" 属性

#### 41. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:135

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 135 行, 第 35 列
- **错误信息**: 无法访问 "float" 类的 "append" 属性
  属性 "append" 未知

#### 42. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:135

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 135 行, 第 35 列
- **错误信息**: 无法访问 "dict[str, str | dict[str, str | None]]" 类的 "append" 属性
  属性 "append" 未知

#### 43. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:150

- **规则**: `reportIndexIssue`
- **位置**: 第 150 行, 第 8 列
- **错误信息**: "bool" 类型上未定义 "__setitem__" 方法

#### 44. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:150

- **规则**: `reportOptionalSubscript`
- **位置**: 第 150 行, 第 8 列
- **错误信息**: `None` 不支持下标访问

#### 45. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:150

- **规则**: `reportIndexIssue`
- **位置**: 第 150 行, 第 8 列
- **错误信息**: "float" 类型上未定义 "__setitem__" 方法

#### 46. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:150

- **规则**: `reportCallIssue`
- **位置**: 第 150 行, 第 8 列
- **错误信息**: "__setitem__" 的重载与提供的参数不匹配

#### 47. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:150

- **规则**: `reportArgumentType`
- **位置**: 第 150 行, 第 8 列
- **错误信息**: "Literal['current_phase']" 类型的实参无法赋值给函数 "__setitem__" 中 "slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['current_phase']" 与 "slice[Any, Any, Any]" 不兼容

#### 48. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:178

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 178 行, 第 39 列
- **错误信息**: 无法访问 "bool" 类的 "append" 属性
  属性 "append" 未知

#### 49. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:178

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 178 行, 第 39 列
- **错误信息**: `None` 没有 "append" 属性

#### 50. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:178

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 178 行, 第 39 列
- **错误信息**: 无法访问 "float" 类的 "append" 属性
  属性 "append" 未知

#### 51. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:178

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 178 行, 第 39 列
- **错误信息**: 无法访问 "dict[str, str | dict[str, str | None]]" 类的 "append" 属性
  属性 "append" 未知

#### 52. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:189

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 189 行, 第 35 列
- **错误信息**: 无法访问 "bool" 类的 "append" 属性
  属性 "append" 未知

#### 53. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:189

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 189 行, 第 35 列
- **错误信息**: `None` 没有 "append" 属性

#### 54. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:189

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 189 行, 第 35 列
- **错误信息**: 无法访问 "float" 类的 "append" 属性
  属性 "append" 未知

#### 55. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:189

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 189 行, 第 35 列
- **错误信息**: 无法访问 "dict[str, str | dict[str, str | None]]" 类的 "append" 属性
  属性 "append" 未知

#### 56. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:204

- **规则**: `reportIndexIssue`
- **位置**: 第 204 行, 第 8 列
- **错误信息**: "bool" 类型上未定义 "__setitem__" 方法

#### 57. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:204

- **规则**: `reportOptionalSubscript`
- **位置**: 第 204 行, 第 8 列
- **错误信息**: `None` 不支持下标访问

#### 58. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:204

- **规则**: `reportIndexIssue`
- **位置**: 第 204 行, 第 8 列
- **错误信息**: "float" 类型上未定义 "__setitem__" 方法

#### 59. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:204

- **规则**: `reportCallIssue`
- **位置**: 第 204 行, 第 8 列
- **错误信息**: "__setitem__" 的重载与提供的参数不匹配

#### 60. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:204

- **规则**: `reportArgumentType`
- **位置**: 第 204 行, 第 8 列
- **错误信息**: "Literal['current_phase']" 类型的实参无法赋值给函数 "__setitem__" 中 "slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['current_phase']" 与 "slice[Any, Any, Any]" 不兼容

#### 61. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:239

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 239 行, 第 39 列
- **错误信息**: 无法访问 "bool" 类的 "append" 属性
  属性 "append" 未知

#### 62. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:239

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 239 行, 第 39 列
- **错误信息**: `None` 没有 "append" 属性

#### 63. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:239

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 239 行, 第 39 列
- **错误信息**: 无法访问 "float" 类的 "append" 属性
  属性 "append" 未知

#### 64. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:239

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 239 行, 第 39 列
- **错误信息**: 无法访问 "dict[str, str | dict[str, str | None]]" 类的 "append" 属性
  属性 "append" 未知

#### 65. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:250

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 250 行, 第 35 列
- **错误信息**: 无法访问 "bool" 类的 "append" 属性
  属性 "append" 未知

#### 66. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:250

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 250 行, 第 35 列
- **错误信息**: `None` 没有 "append" 属性

#### 67. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:250

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 250 行, 第 35 列
- **错误信息**: 无法访问 "float" 类的 "append" 属性
  属性 "append" 未知

#### 68. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:250

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 250 行, 第 35 列
- **错误信息**: 无法访问 "dict[str, str | dict[str, str | None]]" 类的 "append" 属性
  属性 "append" 未知

#### 69. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:269

- **规则**: `reportIndexIssue`
- **位置**: 第 269 行, 第 8 列
- **错误信息**: "bool" 类型上未定义 "__setitem__" 方法

#### 70. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:269

- **规则**: `reportOptionalSubscript`
- **位置**: 第 269 行, 第 8 列
- **错误信息**: `None` 不支持下标访问

#### 71. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:269

- **规则**: `reportIndexIssue`
- **位置**: 第 269 行, 第 8 列
- **错误信息**: "float" 类型上未定义 "__setitem__" 方法

#### 72. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:269

- **规则**: `reportCallIssue`
- **位置**: 第 269 行, 第 8 列
- **错误信息**: "__setitem__" 的重载与提供的参数不匹配

#### 73. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:269

- **规则**: `reportArgumentType`
- **位置**: 第 269 行, 第 8 列
- **错误信息**: "Literal['current_phase']" 类型的实参无法赋值给函数 "__setitem__" 中 "slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['current_phase']" 与 "slice[Any, Any, Any]" 不兼容

#### 74. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:304

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 304 行, 第 35 列
- **错误信息**: 无法访问 "bool" 类的 "append" 属性
  属性 "append" 未知

#### 75. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:304

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 304 行, 第 35 列
- **错误信息**: `None` 没有 "append" 属性

#### 76. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:304

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 304 行, 第 35 列
- **错误信息**: 无法访问 "float" 类的 "append" 属性
  属性 "append" 未知

#### 77. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:304

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 304 行, 第 35 列
- **错误信息**: 无法访问 "dict[str, str | dict[str, str | None]]" 类的 "append" 属性
  属性 "append" 未知

#### 78. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:312

- **规则**: `reportArgumentType`
- **位置**: 第 312 行, 第 16 列
- **错误信息**: "float | dict[str, str | dict[str, str | None]] | list[Unknown] | Literal[True]" 类型的实参无法赋值给函数 "_calculate_duration" 中 "float" 类型的形参 "start_time"
  "float | dict[str, str | dict[str, str | None]] | list[Unknown] | Literal[True]" 类型与 "float" 类型不兼容
    "dict[str, str | dict[str, str | None]]" 与 "float" 不兼容

#### 79. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:319

- **规则**: `reportArgumentType`
- **位置**: 第 319 行, 第 71 列
- **错误信息**: "float | dict[str, str | dict[str, str | None]] | list[Unknown] | Literal[True]" 类型的实参无法赋值给函数 "len" 中 "Sized" 类型的形参 "obj"
  "float | dict[str, str | dict[str, str | None]] | list[Unknown] | Literal[True]" 类型与 "Sized" 类型不兼容
    "float" 与 Protocol 类 "Sized" 不兼容
      "__len__" 不存在

#### 80. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:324

- **规则**: `reportIndexIssue`
- **位置**: 第 324 行, 第 8 列
- **错误信息**: "bool" 类型上未定义 "__setitem__" 方法

#### 81. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:324

- **规则**: `reportOptionalSubscript`
- **位置**: 第 324 行, 第 8 列
- **错误信息**: `None` 不支持下标访问

#### 82. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:324

- **规则**: `reportIndexIssue`
- **位置**: 第 324 行, 第 8 列
- **错误信息**: "float" 类型上未定义 "__setitem__" 方法

#### 83. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:324

- **规则**: `reportCallIssue`
- **位置**: 第 324 行, 第 8 列
- **错误信息**: "__setitem__" 的重载与提供的参数不匹配

#### 84. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:324

- **规则**: `reportArgumentType`
- **位置**: 第 324 行, 第 8 列
- **错误信息**: "Literal['current_phase']" 类型的实参无法赋值给函数 "__setitem__" 中 "slice[Any, Any, Any]" 类型的形参 "key"
  "Literal['current_phase']" 与 "slice[Any, Any, Any]" 不兼容

#### 85. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:82

- **规则**: `reportUnusedVariable`
- **位置**: 第 82 行, 第 20 列
- **错误信息**: 变量 "stderr" 未使用

#### 86. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:151

- **规则**: `reportUnnecessaryIsInstance`
- **位置**: 第 151 行, 第 50 列
- **错误信息**: "type[ResultMessage]" 一定是 "type" 的实例，无需再调用 `isinstance`

#### 87. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:215

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 215 行, 第 40 列
- **错误信息**: 无法访问 "int" 类的 "append" 属性
  属性 "append" 未知

#### 88. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:225

- **规则**: `reportOperatorIssue`
- **位置**: 第 225 行, 第 12 列
- **错误信息**: "int | list[Unknown]" 与 "int" 类型不支持 "+=" 运算符
  "list[Unknown]" 与 "int" 类型不支持 "+" 运算符

#### 89. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:230

- **规则**: `reportOperatorIssue`
- **位置**: 第 230 行, 第 16 列
- **错误信息**: "int | list[Unknown]" 与 "Literal[1]" 类型不支持 "+=" 运算符
  "list[Unknown]" 与 "Literal[1]" 类型不支持 "+" 运算符

#### 90. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:232

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 232 行, 第 40 列
- **错误信息**: 无法访问 "int" 类的 "append" 属性
  属性 "append" 未知

#### 91. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:260

- **规则**: `reportOperatorIssue`
- **位置**: 第 260 行, 第 16 列
- **错误信息**: "int | list[Unknown]" 与 "Literal[1]" 类型不支持 "+=" 运算符
  "list[Unknown]" 与 "Literal[1]" 类型不支持 "+" 运算符

#### 92. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:261

- **规则**: `reportOperatorIssue`
- **位置**: 第 261 行, 第 16 列
- **错误信息**: "int | list[Unknown]" 与 "int" 类型不支持 "+=" 运算符
  "list[Unknown]" 与 "int" 类型不支持 "+" 运算符

#### 93. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:264

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 264 行, 第 36 列
- **错误信息**: 无法访问 "int" 类的 "append" 属性
  属性 "append" 未知

#### 94. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:404

- **规则**: `reportUnusedVariable`
- **位置**: 第 404 行, 第 20 列
- **错误信息**: 变量 "stderr" 未使用

#### 95. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:430

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 430 行, 第 45 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 96. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:641

- **规则**: `reportArgumentType`
- **位置**: 第 641 行, 第 12 列
- **错误信息**: "Dict[str, Any]" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | list[Unknown] | None" 类型的形参 "value"
  "Dict[str, Any]" 类型与 "bool | list[Unknown] | None" 类型不兼容
    "Dict[str, Any]" 与 "bool" 不兼容
    "Dict[str, Any]" 与 "None" 不兼容
    "Dict[str, Any]" 与 "list[Unknown]" 不兼容

#### 97. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:647

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 647 行, 第 43 列
- **错误信息**: 无法访问 "bool" 类的 "append" 属性
  属性 "append" 未知

#### 98. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:647

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 647 行, 第 43 列
- **错误信息**: `None` 没有 "append" 属性

#### 99. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:651

- **规则**: `reportArgumentType`
- **位置**: 第 651 行, 第 12 列
- **错误信息**: "dict[str, bool | str]" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | list[Unknown] | None" 类型的形参 "value"
  "dict[str, bool | str]" 类型与 "bool | list[Unknown] | None" 类型不兼容
    "dict[str, bool | str]" 与 "bool" 不兼容
    "dict[str, bool | str]" 与 "None" 不兼容
    "dict[str, bool | str]" 与 "list[Unknown]" 不兼容

#### 100. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:653

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 653 行, 第 39 列
- **错误信息**: 无法访问 "bool" 类的 "append" 属性
  属性 "append" 未知

#### 101. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:653

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 653 行, 第 39 列
- **错误信息**: `None` 没有 "append" 属性

#### 102. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:663

- **规则**: `reportArgumentType`
- **位置**: 第 663 行, 第 16 列
- **错误信息**: "Dict[str, Any]" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | list[Unknown] | None" 类型的形参 "value"
  "Dict[str, Any]" 类型与 "bool | list[Unknown] | None" 类型不兼容
    "Dict[str, Any]" 与 "bool" 不兼容
    "Dict[str, Any]" 与 "None" 不兼容
    "Dict[str, Any]" 与 "list[Unknown]" 不兼容

#### 103. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:669

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 669 行, 第 47 列
- **错误信息**: 无法访问 "bool" 类的 "append" 属性
  属性 "append" 未知

#### 104. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:669

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 669 行, 第 47 列
- **错误信息**: `None` 没有 "append" 属性

#### 105. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:673

- **规则**: `reportArgumentType`
- **位置**: 第 673 行, 第 16 列
- **错误信息**: "dict[str, bool | str]" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | list[Unknown] | None" 类型的形参 "value"
  "dict[str, bool | str]" 类型与 "bool | list[Unknown] | None" 类型不兼容
    "dict[str, bool | str]" 与 "bool" 不兼容
    "dict[str, bool | str]" 与 "None" 不兼容
    "dict[str, bool | str]" 与 "list[Unknown]" 不兼容

#### 106. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:675

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 675 行, 第 43 列
- **错误信息**: 无法访问 "bool" 类的 "append" 属性
  属性 "append" 未知

#### 107. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:675

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 675 行, 第 43 列
- **错误信息**: `None` 没有 "append" 属性

#### 108. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:685

- **规则**: `reportArgumentType`
- **位置**: 第 685 行, 第 16 列
- **错误信息**: "Dict[str, Any]" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | list[Unknown] | None" 类型的形参 "value"
  "Dict[str, Any]" 类型与 "bool | list[Unknown] | None" 类型不兼容
    "Dict[str, Any]" 与 "bool" 不兼容
    "Dict[str, Any]" 与 "None" 不兼容
    "Dict[str, Any]" 与 "list[Unknown]" 不兼容

#### 109. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:690

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 690 行, 第 47 列
- **错误信息**: 无法访问 "bool" 类的 "append" 属性
  属性 "append" 未知

#### 110. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:690

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 690 行, 第 47 列
- **错误信息**: `None` 没有 "append" 属性

#### 111. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:694

- **规则**: `reportArgumentType`
- **位置**: 第 694 行, 第 16 列
- **错误信息**: "dict[str, bool | str]" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | list[Unknown] | None" 类型的形参 "value"
  "dict[str, bool | str]" 类型与 "bool | list[Unknown] | None" 类型不兼容
    "dict[str, bool | str]" 与 "bool" 不兼容
    "dict[str, bool | str]" 与 "None" 不兼容
    "dict[str, bool | str]" 与 "list[Unknown]" 不兼容

#### 112. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:696

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 696 行, 第 43 列
- **错误信息**: 无法访问 "bool" 类的 "append" 属性
  属性 "append" 未知

#### 113. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:696

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 696 行, 第 43 列
- **错误信息**: `None` 没有 "append" 属性

#### 114. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:36

- **规则**: `reportUnusedImport`
- **位置**: 第 36 行, 第 17 列
- **错误信息**: "_query" 导入项未使用

#### 115. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:37

- **规则**: `reportUnusedImport`
- **位置**: 第 37 行, 第 30 列
- **错误信息**: "_ClaudeAgentOptions" 导入项未使用

#### 116. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:38

- **规则**: `reportUnusedImport`
- **位置**: 第 38 行, 第 25 列
- **错误信息**: "_ResultMessage" 导入项未使用

#### 117. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:62

- **规则**: `reportIndexIssue`
- **位置**: 第 62 行, 第 9 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 118. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:93

- **规则**: `reportIndexIssue`
- **位置**: 第 93 行, 第 37 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 119. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:93

- **规则**: `reportIndexIssue`
- **位置**: 第 93 行, 第 42 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 120. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:94

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 94 行, 第 52 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "generate_test_report" 函数中的 "results" 形参
  参数类型为 "dict[str, str | dict[str, int | float] | list[Unknown]]"

#### 121. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:105

- **规则**: `reportIndexIssue`
- **位置**: 第 105 行, 第 104 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 122. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:109

- **规则**: `reportUnusedVariable`
- **位置**: 第 109 行, 第 12 列
- **错误信息**: 变量 "stdout" 未使用

#### 123. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:109

- **规则**: `reportUnusedVariable`
- **位置**: 第 109 行, 第 20 列
- **错误信息**: 变量 "stderr" 未使用

#### 124. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:127

- **规则**: `reportIndexIssue`
- **位置**: 第 127 行, 第 63 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 125. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:127

- **规则**: `reportIndexIssue`
- **位置**: 第 127 行, 第 68 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 126. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:151

- **规则**: `reportIndexIssue`
- **位置**: 第 151 行, 第 40 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 127. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:151

- **规则**: `reportIndexIssue`
- **位置**: 第 151 行, 第 45 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 128. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:194

- **规则**: `reportUnnecessaryComparison`
- **位置**: 第 194 行, 第 19 列
- **错误信息**: 条件的计算结果始终为 `True`，因为类型 "type[ResultMessage]" 和 "None" 之间不存在交集

#### 129. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:194

- **规则**: `reportUnnecessaryIsInstance`
- **位置**: 第 194 行, 第 50 列
- **错误信息**: "type[ResultMessage]" 一定是 "type" 的实例，无需再调用 `isinstance`

#### 130. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:226

- **规则**: `reportIndexIssue`
- **位置**: 第 226 行, 第 50 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 131. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:226

- **规则**: `reportIndexIssue`
- **位置**: 第 226 行, 第 55 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 132. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:262

- **规则**: `reportIndexIssue`
- **位置**: 第 262 行, 第 66 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 133. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:262

- **规则**: `reportIndexIssue`
- **位置**: 第 262 行, 第 85 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 134. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:277

- **规则**: `reportUnusedImport`
- **位置**: 第 277 行, 第 19 列
- **错误信息**: "debugpy" 导入项未使用

#### 135. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:314

- **规则**: `reportIndexIssue`
- **位置**: 第 314 行, 第 9 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 136. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:379

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 379 行, 第 64 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 137. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:381

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 381 行, 第 46 列
- **错误信息**: 参数类型未知
  实参对应于 "invoke_debugpy" 函数中的 "test_file" 形参

#### 138. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:381

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 381 行, 第 71 列
- **错误信息**: 参数类型未知
  实参对应于 "invoke_debugpy" 函数中的 "error_details" 形参

#### 139. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:421

- **规则**: `reportIndexIssue`
- **位置**: 第 421 行, 第 44 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 140. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:421

- **规则**: `reportIndexIssue`
- **位置**: 第 421 行, 第 70 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 141. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:421

- **规则**: `reportIndexIssue`
- **位置**: 第 421 行, 第 75 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\agents.py`
3. `..\autoBMAD\epic_automation\dev_agent.py`
4. `..\autoBMAD\epic_automation\epic_driver.py`
5. `..\autoBMAD\epic_automation\init_db.py`
6. `..\autoBMAD\epic_automation\log_manager.py`
7. `..\autoBMAD\epic_automation\qa_agent.py`
8. `..\autoBMAD\epic_automation\qa_tools_integration.py`
9. `..\autoBMAD\epic_automation\quality_agents.py`
10. `..\autoBMAD\epic_automation\sdk_session_manager.py`
11. `..\autoBMAD\epic_automation\sdk_wrapper.py`
12. `..\autoBMAD\epic_automation\sm_agent.py`
13. `..\autoBMAD\epic_automation\state_manager.py`
14. `..\autoBMAD\epic_automation\test_automation_agent.py`
15. `..\autoBMAD\epic_automation\test_logging.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:18:33 - error: "Message" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:109:37 - error: 类型表达式中不允许使用变量 (reportInvalidTypeForm)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:111:37 - error: 参数类型未知
    实参对应于 "getattr" 函数中的 "o" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:113:41 - error: 参数类型未知
    实参对应于 "getattr" 函数中的 "o" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:355:24 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:357:26 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:406:24 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:408:26 - error: 参数类型未知
    实参对应于 "hasattr" 函数中的 "obj" 形参 (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:77:12 - error: "str" 与 "bool | float | dict[str, str | dict[str, str | None]] | list[Unknown] | None" 类型不支持 "in" 运算符
    "str" 与 "bool" 类型不支持 "in" 运算符
    "str" 与 "None" 类型不支持 "in" 运算符
    "str" 与 "float" 类型不支持 "in" 运算符 (reportOperatorIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:78:13 - error: "bool" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:78:13 - error: `None` 不支持下标访问 (reportOptionalSubscript)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:78:13 - error: "float" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:78:13 - error: "__getitem__" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:78:13 - error: "str" 类型的实参无法赋值给函数 "__getitem__" 中 "slice[Any, Any, Any]" 类型的形参 "s"
    "str" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:78:13 - error: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:80:17 - error: "bool" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:80:17 - error: `None` 不支持下标访问 (reportOptionalSubscript)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:80:17 - error: "float" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:80:17 - error: "__getitem__" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:80:17 - error: "str" 类型的实参无法赋值给函数 "__getitem__" 中 "slice[Any, Any, Any]" 类型的形参 "s"
    "str" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:80:17 - error: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:80:17 - error: "float" 类型的实参无法赋值给函数 "__setitem__" 中 "str | None" 类型的形参 "value"
    "float" 类型与 "str | None" 类型不兼容
      "float" 与 "str" 不兼容
      "float" 与 "None" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:82:17 - error: "bool" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:82:17 - error: `None` 不支持下标访问 (reportOptionalSubscript)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:82:17 - error: "float" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:82:17 - error: "__getitem__" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:82:17 - error: "str" 类型的实参无法赋值给函数 "__getitem__" 中 "slice[Any, Any, Any]" 类型的形参 "s"
    "str" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:82:17 - error: "str" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:82:17 - error: "float" 类型的实参无法赋值给函数 "__setitem__" 中 "str | None" 类型的形参 "value"
    "float" 类型与 "str | None" 类型不兼容
      "float" 与 "str" 不兼容
      "float" 与 "None" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:96:9 - error: "bool" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:96:9 - error: `None` 不支持下标访问 (reportOptionalSubscript)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:96:9 - error: "float" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:96:9 - error: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:96:9 - error: "Literal['current_phase']" 类型的实参无法赋值给函数 "__setitem__" 中 "slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['current_phase']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:124:40 - error: 无法访问 "bool" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:124:40 - error: `None` 没有 "append" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:124:40 - error: 无法访问 "float" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:124:40 - error: 无法访问 "dict[str, str | dict[str, str | None]]" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:135:36 - error: 无法访问 "bool" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:135:36 - error: `None` 没有 "append" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:135:36 - error: 无法访问 "float" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:135:36 - error: 无法访问 "dict[str, str | dict[str, str | None]]" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:150:9 - error: "bool" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:150:9 - error: `None` 不支持下标访问 (reportOptionalSubscript)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:150:9 - error: "float" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:150:9 - error: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:150:9 - error: "Literal['current_phase']" 类型的实参无法赋值给函数 "__setitem__" 中 "slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['current_phase']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:178:40 - error: 无法访问 "bool" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:178:40 - error: `None` 没有 "append" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:178:40 - error: 无法访问 "float" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:178:40 - error: 无法访问 "dict[str, str | dict[str, str | None]]" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:189:36 - error: 无法访问 "bool" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:189:36 - error: `None` 没有 "append" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:189:36 - error: 无法访问 "float" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:189:36 - error: 无法访问 "dict[str, str | dict[str, str | None]]" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:204:9 - error: "bool" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:204:9 - error: `None` 不支持下标访问 (reportOptionalSubscript)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:204:9 - error: "float" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:204:9 - error: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:204:9 - error: "Literal['current_phase']" 类型的实参无法赋值给函数 "__setitem__" 中 "slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['current_phase']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:239:40 - error: 无法访问 "bool" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:239:40 - error: `None` 没有 "append" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:239:40 - error: 无法访问 "float" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:239:40 - error: 无法访问 "dict[str, str | dict[str, str | None]]" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:250:36 - error: 无法访问 "bool" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:250:36 - error: `None` 没有 "append" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:250:36 - error: 无法访问 "float" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:250:36 - error: 无法访问 "dict[str, str | dict[str, str | None]]" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:269:9 - error: "bool" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:269:9 - error: `None` 不支持下标访问 (reportOptionalSubscript)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:269:9 - error: "float" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:269:9 - error: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:269:9 - error: "Literal['current_phase']" 类型的实参无法赋值给函数 "__setitem__" 中 "slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['current_phase']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:304:36 - error: 无法访问 "bool" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:304:36 - error: `None` 没有 "append" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:304:36 - error: 无法访问 "float" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:304:36 - error: 无法访问 "dict[str, str | dict[str, str | None]]" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:312:17 - error: "float | dict[str, str | dict[str, str | None]] | list[Unknown] | Literal[True]" 类型的实参无法赋值给函数 "_calculate_duration" 中 "float" 类型的形参 "start_time"
    "float | dict[str, str | dict[str, str | None]] | list[Unknown] | Literal[True]" 类型与 "float" 类型不兼容
      "dict[str, str | dict[str, str | None]]" 与 "float" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:319:72 - error: "float | dict[str, str | dict[str, str | None]] | list[Unknown] | Literal[True]" 类型的实参无法赋值给函数 "len" 中 "Sized" 类型的形参 "obj"
    "float | dict[str, str | dict[str, str | None]] | list[Unknown] | Literal[True]" 类型与 "Sized" 类型不兼容
      "float" 与 Protocol 类 "Sized" 不兼容
        "__len__" 不存在 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:324:9 - error: "bool" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:324:9 - error: `None` 不支持下标访问 (reportOptionalSubscript)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:324:9 - error: "float" 类型上未定义 "__setitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:324:9 - error: "__setitem__" 的重载与提供的参数不匹配 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:324:9 - error: "Literal['current_phase']" 类型的实参无法赋值给函数 "__setitem__" 中 "slice[Any, Any, Any]" 类型的形参 "key"
    "Literal['current_phase']" 与 "slice[Any, Any, Any]" 不兼容 (reportArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:82:21 - error: 变量 "stderr" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:151:51 - error: "type[ResultMessage]" 一定是 "type" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:215:41 - error: 无法访问 "int" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:225:13 - error: "int | list[Unknown]" 与 "int" 类型不支持 "+=" 运算符
    "list[Unknown]" 与 "int" 类型不支持 "+" 运算符 (reportOperatorIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:230:17 - error: "int | list[Unknown]" 与 "Literal[1]" 类型不支持 "+=" 运算符
    "list[Unknown]" 与 "Literal[1]" 类型不支持 "+" 运算符 (reportOperatorIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:232:41 - error: 无法访问 "int" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:260:17 - error: "int | list[Unknown]" 与 "Literal[1]" 类型不支持 "+=" 运算符
    "list[Unknown]" 与 "Literal[1]" 类型不支持 "+" 运算符 (reportOperatorIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:261:17 - error: "int | list[Unknown]" 与 "int" 类型不支持 "+=" 运算符
    "list[Unknown]" 与 "int" 类型不支持 "+" 运算符 (reportOperatorIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:264:37 - error: 无法访问 "int" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:404:21 - error: 变量 "stderr" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:430:46 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:641:13 - error: "Dict[str, Any]" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | list[Unknown] | None" 类型的形参 "value"
    "Dict[str, Any]" 类型与 "bool | list[Unknown] | None" 类型不兼容
      "Dict[str, Any]" 与 "bool" 不兼容
      "Dict[str, Any]" 与 "None" 不兼容
      "Dict[str, Any]" 与 "list[Unknown]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:647:44 - error: 无法访问 "bool" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:647:44 - error: `None` 没有 "append" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:651:13 - error: "dict[str, bool | str]" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | list[Unknown] | None" 类型的形参 "value"
    "dict[str, bool | str]" 类型与 "bool | list[Unknown] | None" 类型不兼容
      "dict[str, bool | str]" 与 "bool" 不兼容
      "dict[str, bool | str]" 与 "None" 不兼容
      "dict[str, bool | str]" 与 "list[Unknown]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:653:40 - error: 无法访问 "bool" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:653:40 - error: `None` 没有 "append" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:663:17 - error: "Dict[str, Any]" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | list[Unknown] | None" 类型的形参 "value"
    "Dict[str, Any]" 类型与 "bool | list[Unknown] | None" 类型不兼容
      "Dict[str, Any]" 与 "bool" 不兼容
      "Dict[str, Any]" 与 "None" 不兼容
      "Dict[str, Any]" 与 "list[Unknown]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:669:48 - error: 无法访问 "bool" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:669:48 - error: `None` 没有 "append" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:673:17 - error: "dict[str, bool | str]" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | list[Unknown] | None" 类型的形参 "value"
    "dict[str, bool | str]" 类型与 "bool | list[Unknown] | None" 类型不兼容
      "dict[str, bool | str]" 与 "bool" 不兼容
      "dict[str, bool | str]" 与 "None" 不兼容
      "dict[str, bool | str]" 与 "list[Unknown]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:675:44 - error: 无法访问 "bool" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:675:44 - error: `None` 没有 "append" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:685:17 - error: "Dict[str, Any]" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | list[Unknown] | None" 类型的形参 "value"
    "Dict[str, Any]" 类型与 "bool | list[Unknown] | None" 类型不兼容
      "Dict[str, Any]" 与 "bool" 不兼容
      "Dict[str, Any]" 与 "None" 不兼容
      "Dict[str, Any]" 与 "list[Unknown]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:690:48 - error: 无法访问 "bool" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:690:48 - error: `None` 没有 "append" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:694:17 - error: "dict[str, bool | str]" 类型的实参无法赋值给函数 "__setitem__" 中 "bool | list[Unknown] | None" 类型的形参 "value"
    "dict[str, bool | str]" 类型与 "bool | list[Unknown] | None" 类型不兼容
      "dict[str, bool | str]" 与 "bool" 不兼容
      "dict[str, bool | str]" 与 "None" 不兼容
      "dict[str, bool | str]" 与 "list[Unknown]" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:696:44 - error: 无法访问 "bool" 类的 "append" 属性
    属性 "append" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:696:44 - error: `None` 没有 "append" 属性 (reportOptionalMemberAccess)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:36:18 - error: "_query" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:37:31 - error: "_ClaudeAgentOptions" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:38:26 - error: "_ResultMessage" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:62:10 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:93:38 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:93:43 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:94:53 - error: 部分参数的类型未知
    实参对应于 "generate_test_report" 函数中的 "results" 形参
    参数类型为 "dict[str, str | dict[str, int | float] | list[Unknown]]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:105:105 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:109:13 - error: 变量 "stdout" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:109:21 - error: 变量 "stderr" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:127:64 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:127:69 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:151:41 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:151:46 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:194:20 - error: 条件的计算结果始终为 `True`，因为类型 "type[ResultMessage]" 和 "None" 之间不存在交集 (reportUnnecessaryComparison)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:194:51 - error: "type[ResultMessage]" 一定是 "type" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:226:51 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:226:56 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:262:67 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:262:86 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:277:20 - error: "debugpy" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:314:10 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:379:65 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:381:47 - error: 参数类型未知
    实参对应于 "invoke_debugpy" 函数中的 "test_file" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:381:72 - error: 参数类型未知
    实参对应于 "invoke_debugpy" 函数中的 "error_details" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:421:45 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:421:71 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:421:76 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
141 errors, 0 warnings, 0 notes
```


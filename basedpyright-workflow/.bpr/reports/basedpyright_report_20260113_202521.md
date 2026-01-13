# BasedPyright 检查报告
**生成时间**: 2026-01-13 20:25:21
**检查时间**: 2026-01-13T20:25:19.328086
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 41 |
| ❌ 错误 (Error) | 219 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.26 秒 |

## 🔴 错误详情

共发现 **219** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py`: 85 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py`: 46 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py`: 37 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py`: 21 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py`: 9 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\doc_parser.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\config.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\__init__.py`: 1 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py`: 1 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent_old.py`: 1 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\base_controller.py`: 1 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py`: 1 个错误

### 按规则分组

- `reportPrivateUsage`: 47 次
- `reportIndexIssue`: 32 次
- `reportUnknownArgumentType`: 24 次
- `reportAttributeAccessIssue`: 18 次
- `reportMissingParameterType`: 18 次
- `reportUnusedImport`: 16 次
- `reportUnknownParameterType`: 16 次
- `reportAbstractUsage`: 10 次
- `reportArgumentType`: 8 次
- `reportOptionalMemberAccess`: 6 次
- `reportUndefinedVariable`: 6 次
- `reportUnusedVariable`: 6 次
- `reportGeneralTypeIssues`: 4 次
- `reportMissingTypeArgument`: 3 次
- `reportUnknownLambdaType`: 2 次
- `reportPossiblyUnboundVariable`: 1 次
- `reportCallIssue`: 1 次
- `reportOperatorIssue`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\__init__.py:7

- **规则**: `reportUnusedImport`
- **位置**: 第 7 行, 第 20 列
- **错误信息**: "quality_agents" 导入项未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:7

- **规则**: `reportUnusedImport`
- **位置**: 第 7 行, 第 7 列
- **错误信息**: "os" 导入项未使用

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:12

- **规则**: `reportUnusedImport`
- **位置**: 第 12 行, 第 21 列
- **错误信息**: "abstractmethod" 导入项未使用

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:20

- **规则**: `reportUnusedImport`
- **位置**: 第 20 行, 第 11 列
- **错误信息**: "anthropic" 导入项未使用

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:113

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 113 行, 第 34 列
- **错误信息**: `None` 没有 "model" 属性

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:114

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 114 行, 第 39 列
- **错误信息**: `None` 没有 "max_tokens" 属性

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:115

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 115 行, 第 40 列
- **错误信息**: `None` 没有 "temperature" 属性

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:122

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 122 行, 第 48 列
- **错误信息**: 无法访问 "ThinkingBlock" 类的 "text" 属性
  属性 "text" 未知

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:122

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 122 行, 第 48 列
- **错误信息**: 无法访问 "RedactedThinkingBlock" 类的 "text" 属性
  属性 "text" 未知

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:122

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 122 行, 第 48 列
- **错误信息**: 无法访问 "ToolUseBlock" 类的 "text" 属性
  属性 "text" 未知

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:122

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 122 行, 第 48 列
- **错误信息**: 无法访问 "ServerToolUseBlock" 类的 "text" 属性
  属性 "text" 未知

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:122

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 122 行, 第 48 列
- **错误信息**: 无法访问 "WebSearchToolResultBlock" 类的 "text" 属性
  属性 "text" 未知

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:124

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 124 行, 第 37 列
- **错误信息**: `None` 没有 "model" 属性

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:130

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 130 行, 第 37 列
- **错误信息**: `None` 没有 "model" 属性

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:153

- **规则**: `reportUnknownParameterType`
- **位置**: 第 153 行, 第 23 列
- **错误信息**: "exc_type" 参数的类型未知

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:153

- **规则**: `reportMissingParameterType`
- **位置**: 第 153 行, 第 23 列
- **错误信息**: "exc_type" 参数缺少类型注解

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:153

- **规则**: `reportUnknownParameterType`
- **位置**: 第 153 行, 第 33 列
- **错误信息**: "exc_val" 参数的类型未知

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:153

- **规则**: `reportMissingParameterType`
- **位置**: 第 153 行, 第 33 列
- **错误信息**: "exc_val" 参数缺少类型注解

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:153

- **规则**: `reportUnknownParameterType`
- **位置**: 第 153 行, 第 42 列
- **错误信息**: "exc_tb" 参数的类型未知

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:153

- **规则**: `reportMissingParameterType`
- **位置**: 第 153 行, 第 42 列
- **错误信息**: "exc_tb" 参数缺少类型注解

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:156

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 156 行, 第 24 列
- **错误信息**: `None` 没有 "close" 属性

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:215

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 215 行, 第 24 列
- **错误信息**: 无法访问 "BrokenWorkerInterpreter" 类的 "started" 属性
  属性 "started" 未知

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\config.py:99

- **规则**: `reportUnknownParameterType`
- **位置**: 第 99 行, 第 8 列
- **错误信息**: "suggestions" 参数的类型部分未知
  参数为 "list[Unknown] | None" 类型

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\config.py:99

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 99 行, 第 30 列
- **错误信息**: "list" 泛型类应有类型参数

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:108

- **规则**: `reportArgumentType`
- **位置**: 第 108 行, 第 24 列
- **错误信息**: "int | bool | str" 类型的实参无法赋值给函数 "__init__" 中 "int" 类型的形参 "timeout"
  "int | bool | str" 类型与 "int" 类型不兼容
    "str" 与 "int" 不兼容

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:109

- **规则**: `reportArgumentType`
- **位置**: 第 109 行, 第 25 列
- **错误信息**: "int | bool | str" 类型的实参无法赋值给函数 "__init__" 中 "bool" 类型的形参 "parallel"
  "int | bool | str" 类型与 "bool" 类型不兼容
    "int" 与 "bool" 不兼容

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:111

- **规则**: `reportArgumentType`
- **位置**: 第 111 行, 第 25 列
- **错误信息**: "int | bool | str" 类型的实参无法赋值给函数 "__init__" 中 "bool" 类型的形参 "blocking"
  "int | bool | str" 类型与 "bool" 类型不兼容
    "int" 与 "bool" 不兼容

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:112

- **规则**: `reportArgumentType`
- **位置**: 第 112 行, 第 25 列
- **错误信息**: "int | bool | str" 类型的实参无法赋值给函数 "__init__" 中 "int" 类型的形参 "priority"
  "int | bool | str" 类型与 "int" 类型不兼容
    "str" 与 "int" 不兼容

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:120

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 120 行, 第 32 列
- **错误信息**: "b" 参数的类型未知

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:120

- **规则**: `reportUnknownLambdaType`
- **位置**: 第 120 行, 第 35 列
- **错误信息**: 该 `lambda` 的返回类型未知

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:122

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 122 行, 第 60 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:187

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 187 行, 第 28 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 33. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:264

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 264 行, 第 15 列
- **错误信息**: "asyncio" 可能未绑定

#### 34. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:8

- **规则**: `reportUnusedImport`
- **位置**: 第 8 行, 第 7 列
- **错误信息**: "json" 导入项未使用

#### 35. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:890

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 890 行, 第 58 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "join" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

#### 36. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:901

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 901 行, 第 50 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "join" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

#### 37. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent.py:14

- **规则**: `reportUnusedImport`
- **位置**: 第 14 行, 第 48 列
- **错误信息**: "Optional" 导入项未使用

#### 38. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent.py:290

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 290 行, 第 29 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 39. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent.py:295

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 295 行, 第 34 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 40. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent_old.py:62

- **规则**: `reportCallIssue`
- **位置**: 第 62 行, 第 25 列
- **错误信息**: "name" 参数不存在

#### 41. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\base_controller.py:7

- **规则**: `reportUnusedImport`
- **位置**: 第 7 行, 第 7 列
- **错误信息**: "asyncio" 导入项未使用

#### 42. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\doc_parser.py:7

- **规则**: `reportUnusedImport`
- **位置**: 第 7 行, 第 36 列
- **错误信息**: "Optional" 导入项未使用

#### 43. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\doc_parser.py:56

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 56 行, 第 58 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "join" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

#### 44. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\doc_parser.py:63

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 63 行, 第 50 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "join" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

#### 45. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:352

- **规则**: `reportUnusedImport`
- **位置**: 第 352 行, 第 19 列
- **错误信息**: "subprocess" 导入项未使用

#### 46. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:398

- **规则**: `reportUndefinedVariable`
- **位置**: 第 398 行, 第 27 列
- **错误信息**: "PytestAgent" 未定义

#### 47. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:440

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 440 行, 第 42 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 48. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:764

- **规则**: `reportUnusedVariable`
- **位置**: 第 764 行, 第 20 列
- **错误信息**: 变量 "placeholders" 未使用

#### 49. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:983

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 983 行, 第 57 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 50. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:1048

- **规则**: `reportUnusedVariable`
- **位置**: 第 1048 行, 第 21 列
- **错误信息**: 变量 "version" 未使用

#### 51. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:8

- **规则**: `reportUnusedImport`
- **位置**: 第 8 行, 第 7 列
- **错误信息**: "asyncio" 导入项未使用

#### 52. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:11

- **规则**: `reportUnusedImport`
- **位置**: 第 11 行, 第 39 列
- **错误信息**: "MagicMock" 导入项未使用

#### 53. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:21

- **规则**: `reportMissingParameterType`
- **位置**: 第 21 行, 第 23 列
- **错误信息**: "config_or_name" 参数缺少类型注解

#### 54. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:21

- **规则**: `reportMissingParameterType`
- **位置**: 第 21 行, 第 44 列
- **错误信息**: "task_group" 参数缺少类型注解

#### 55. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:21

- **规则**: `reportMissingParameterType`
- **位置**: 第 21 行, 第 61 列
- **错误信息**: "log_manager" 参数缺少类型注解

#### 56. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:26

- **规则**: `reportUnknownParameterType`
- **位置**: 第 26 行, 第 14 列
- **错误信息**: 返回类型 "dict[Unknown, Unknown]" 部分未知

#### 57. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:26

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 26 行, 第 56 列
- **错误信息**: "dict" 泛型类应有类型参数

#### 58. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:185

- **规则**: `reportPrivateUsage`
- **位置**: 第 185 行, 第 21 列
- **错误信息**: "_log_manager" 在声明它受到保护的类之外被使用

#### 59. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:211

- **规则**: `reportUnknownParameterType`
- **位置**: 第 211 行, 第 44 列
- **错误信息**: "mock_anthropic" 参数的类型未知

#### 60. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:211

- **规则**: `reportMissingParameterType`
- **位置**: 第 211 行, 第 44 列
- **错误信息**: "mock_anthropic" 参数缺少类型注解

#### 61. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:223

- **规则**: `reportUnknownParameterType`
- **位置**: 第 223 行, 第 47 列
- **错误信息**: "mock_anthropic" 参数的类型未知

#### 62. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:223

- **规则**: `reportMissingParameterType`
- **位置**: 第 223 行, 第 47 列
- **错误信息**: "mock_anthropic" 参数缺少类型注解

#### 63. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:232

- **规则**: `reportUnknownParameterType`
- **位置**: 第 232 行, 第 51 列
- **错误信息**: "mock_anthropic" 参数的类型未知

#### 64. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:232

- **规则**: `reportMissingParameterType`
- **位置**: 第 232 行, 第 51 列
- **错误信息**: "mock_anthropic" 参数缺少类型注解

#### 65. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:266

- **规则**: `reportUnknownParameterType`
- **位置**: 第 266 行, 第 50 列
- **错误信息**: "mock_read_text" 参数的类型未知

#### 66. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:266

- **规则**: `reportMissingParameterType`
- **位置**: 第 266 行, 第 50 列
- **错误信息**: "mock_read_text" 参数缺少类型注解

#### 67. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:266

- **规则**: `reportUnknownParameterType`
- **位置**: 第 266 行, 第 66 列
- **错误信息**: "mock_exists" 参数的类型未知

#### 68. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:266

- **规则**: `reportMissingParameterType`
- **位置**: 第 266 行, 第 66 列
- **错误信息**: "mock_exists" 参数缺少类型注解

#### 69. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:274

- **规则**: `reportUnusedVariable`
- **位置**: 第 274 行, 第 8 列
- **错误信息**: 变量 "expected_path" 未使用

#### 70. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:281

- **规则**: `reportUnknownParameterType`
- **位置**: 第 281 行, 第 54 列
- **错误信息**: "mock_read_text" 参数的类型未知

#### 71. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:281

- **规则**: `reportMissingParameterType`
- **位置**: 第 281 行, 第 54 列
- **错误信息**: "mock_read_text" 参数缺少类型注解

#### 72. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:281

- **规则**: `reportUnknownParameterType`
- **位置**: 第 281 行, 第 70 列
- **错误信息**: "mock_exists" 参数的类型未知

#### 73. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:281

- **规则**: `reportMissingParameterType`
- **位置**: 第 281 行, 第 70 列
- **错误信息**: "mock_exists" 参数缺少类型注解

#### 74. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:292

- **规则**: `reportUnknownParameterType`
- **位置**: 第 292 行, 第 54 列
- **错误信息**: "mock_exists" 参数的类型未知

#### 75. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:292

- **规则**: `reportMissingParameterType`
- **位置**: 第 292 行, 第 54 列
- **错误信息**: "mock_exists" 参数缺少类型注解

#### 76. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:343

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 343 行, 第 19 列
- **错误信息**: "MockAgent" 类型的对象不能用于 `async with` 语句，因为它未实现 "__aenter__"
  属性 "__aenter__" 未知

#### 77. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:343

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 343 行, 第 19 列
- **错误信息**: "MockAgent" 类型的对象不能用于 `with` 语句，因为它未实现 "__aexit__"
  属性 "__aexit__" 未知

#### 78. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:351

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 351 行, 第 19 列
- **错误信息**: "MockAgent" 类型的对象不能用于 `async with` 语句，因为它未实现 "__aenter__"
  属性 "__aenter__" 未知

#### 79. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:351

- **规则**: `reportGeneralTypeIssues`
- **位置**: 第 351 行, 第 19 列
- **错误信息**: "MockAgent" 类型的对象不能用于 `with` 语句，因为它未实现 "__aexit__"
  属性 "__aexit__" 未知

#### 80. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:382

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 382 行, 第 24 列
- **错误信息**: 参数类型未知
  实参对应于 "callable" 函数中的 "obj" 形参

#### 81. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:382

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 382 行, 第 30 列
- **错误信息**: 无法访问 "MockAgent" 类的 "exit" 属性
  属性 "exit" 未知

#### 82. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:389

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 389 行, 第 18 列
- **错误信息**: 无法访问 "MockAgent" 类的 "exit" 属性
  属性 "exit" 未知

#### 83. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:408

- **规则**: `reportPrivateUsage`
- **位置**: 第 408 行, 第 32 列
- **错误信息**: "_execution_context" 在声明它受到保护的类之外被使用

#### 84. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:450

- **规则**: `reportUnusedVariable`
- **位置**: 第 450 行, 第 8 列
- **错误信息**: 变量 "result1" 未使用

#### 85. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:451

- **规则**: `reportUnusedVariable`
- **位置**: 第 451 行, 第 8 列
- **错误信息**: 变量 "result2" 未使用

#### 86. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:467

- **规则**: `reportUnknownParameterType`
- **位置**: 第 467 行, 第 22 列
- **错误信息**: 返回类型 "dict[Unknown, Unknown]" 部分未知

#### 87. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:467

- **规则**: `reportMissingTypeArgument`
- **位置**: 第 467 行, 第 64 列
- **错误信息**: "dict" 泛型类应有类型参数

#### 88. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:478

- **规则**: `reportArgumentType`
- **位置**: 第 478 行, 第 26 列
- **错误信息**: "Literal[123]" 类型的实参无法赋值给函数 "__init__" 中 "AgentConfig | str | None" 类型的形参 "config_or_name"
  "Literal[123]" 类型与 "AgentConfig | str | None" 类型不兼容
    "Literal[123]" 与 "AgentConfig" 不兼容
    "Literal[123]" 与 "str" 不兼容
    "Literal[123]" 与 "None" 不兼容

#### 89. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:22

- **规则**: `reportMissingParameterType`
- **位置**: 第 22 行, 第 29 列
- **错误信息**: "args" 参数缺少类型注解

#### 90. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:22

- **规则**: `reportMissingParameterType`
- **位置**: 第 22 行, 第 37 列
- **错误信息**: "kwargs" 参数缺少类型注解

#### 91. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:43

- **规则**: `reportArgumentType`
- **位置**: 第 43 行, 第 36 列
- **错误信息**: "None" 类型的实参无法赋值给函数 "__init__" 中 "TaskGroup" 类型的形参 "task_group"
  "None" 与 "TaskGroup" 不兼容

#### 92. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:63

- **规则**: `reportPrivateUsage`
- **位置**: 第 63 行, 第 34 列
- **错误信息**: "_execute_within_taskgroup" 在声明它受到保护的类之外被使用

#### 93. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:77

- **规则**: `reportPrivateUsage`
- **位置**: 第 77 行, 第 34 列
- **错误信息**: "_execute_within_taskgroup" 在声明它受到保护的类之外被使用

#### 94. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:84

- **规则**: `reportArgumentType`
- **位置**: 第 84 行, 第 36 列
- **错误信息**: "None" 类型的实参无法赋值给函数 "__init__" 中 "TaskGroup" 类型的形参 "task_group"
  "None" 与 "TaskGroup" 不兼容

#### 95. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:90

- **规则**: `reportPrivateUsage`
- **位置**: 第 90 行, 第 29 列
- **错误信息**: "_execute_within_taskgroup" 在声明它受到保护的类之外被使用

#### 96. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:97

- **规则**: `reportUndefinedVariable`
- **位置**: 第 97 行, 第 13 列
- **错误信息**: "patch" 未定义

#### 97. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:98

- **规则**: `reportPrivateUsage`
- **位置**: 第 98 行, 第 23 列
- **错误信息**: "_log_execution" 在声明它受到保护的类之外被使用

#### 98. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:107

- **规则**: `reportUndefinedVariable`
- **位置**: 第 107 行, 第 13 列
- **错误信息**: "patch" 未定义

#### 99. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:108

- **规则**: `reportPrivateUsage`
- **位置**: 第 108 行, 第 23 列
- **错误信息**: "_log_execution" 在声明它受到保护的类之外被使用

#### 100. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:117

- **规则**: `reportUndefinedVariable`
- **位置**: 第 117 行, 第 13 列
- **错误信息**: "patch" 未定义

#### 101. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:118

- **规则**: `reportPrivateUsage`
- **位置**: 第 118 行, 第 23 列
- **错误信息**: "_log_execution" 在声明它受到保护的类之外被使用

#### 102. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:127

- **规则**: `reportUndefinedVariable`
- **位置**: 第 127 行, 第 13 列
- **错误信息**: "patch" 未定义

#### 103. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:128

- **规则**: `reportPrivateUsage`
- **位置**: 第 128 行, 第 23 列
- **错误信息**: "_log_execution" 在声明它受到保护的类之外被使用

#### 104. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:139

- **规则**: `reportAbstractUsage`
- **位置**: 第 139 行, 第 21 列
- **错误信息**: 抽象类 "StateDrivenController" 不可实例化
  未实现 "BaseController.execute"
  未实现 "StateDrivenController._make_decision"

#### 105. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:147

- **规则**: `reportAbstractUsage`
- **位置**: 第 147 行, 第 21 列
- **错误信息**: 抽象类 "StateDrivenController" 不可实例化
  未实现 "BaseController.execute"
  未实现 "StateDrivenController._make_decision"

#### 106. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:156

- **规则**: `reportAbstractUsage`
- **位置**: 第 156 行, 第 21 列
- **错误信息**: 抽象类 "StateDrivenController" 不可实例化
  未实现 "BaseController.execute"
  未实现 "StateDrivenController._make_decision"

#### 107. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:159

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 159 行, 第 19 列
- **错误信息**: 无法为 "StateDrivenController" 类的 "make_decision" 属性赋值
  属性 "make_decision" 未知

#### 108. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:169

- **规则**: `reportAbstractUsage`
- **位置**: 第 169 行, 第 21 列
- **错误信息**: 抽象类 "StateDrivenController" 不可实例化
  未实现 "BaseController.execute"
  未实现 "StateDrivenController._make_decision"

#### 109. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:172

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 172 行, 第 19 列
- **错误信息**: 无法为 "StateDrivenController" 类的 "make_decision" 属性赋值
  属性 "make_decision" 未知

#### 110. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:178

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 178 行, 第 26 列
- **错误信息**: 无法访问 "StateDrivenController" 类的 "make_decision" 属性
  属性 "make_decision" 未知

#### 111. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:184

- **规则**: `reportAbstractUsage`
- **位置**: 第 184 行, 第 21 列
- **错误信息**: 抽象类 "StateDrivenController" 不可实例化
  未实现 "BaseController.execute"
  未实现 "StateDrivenController._make_decision"

#### 112. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:187

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 187 行, 第 19 列
- **错误信息**: 无法为 "StateDrivenController" 类的 "make_decision" 属性赋值
  属性 "make_decision" 未知

#### 113. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:192

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 192 行, 第 19 列
- **错误信息**: 无法访问 "StateDrivenController" 类的 "make_decision" 属性
  属性 "make_decision" 未知

#### 114. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:198

- **规则**: `reportAbstractUsage`
- **位置**: 第 198 行, 第 21 列
- **错误信息**: 抽象类 "StateDrivenController" 不可实例化
  未实现 "BaseController.execute"
  未实现 "StateDrivenController._make_decision"

#### 115. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:201

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 201 行, 第 19 列
- **错误信息**: 无法为 "StateDrivenController" 类的 "make_decision" 属性赋值
  属性 "make_decision" 未知

#### 116. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:211

- **规则**: `reportAbstractUsage`
- **位置**: 第 211 行, 第 21 列
- **错误信息**: 抽象类 "StateDrivenController" 不可实例化
  未实现 "BaseController.execute"
  未实现 "StateDrivenController._make_decision"

#### 117. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:213

- **规则**: `reportPrivateUsage`
- **位置**: 第 213 行, 第 26 列
- **错误信息**: "_is_termination_state" 在声明它受到保护的类之外被使用

#### 118. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:214

- **规则**: `reportPrivateUsage`
- **位置**: 第 214 行, 第 26 列
- **错误信息**: "_is_termination_state" 在声明它受到保护的类之外被使用

#### 119. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:215

- **规则**: `reportPrivateUsage`
- **位置**: 第 215 行, 第 26 列
- **错误信息**: "_is_termination_state" 在声明它受到保护的类之外被使用

#### 120. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:216

- **规则**: `reportPrivateUsage`
- **位置**: 第 216 行, 第 26 列
- **错误信息**: "_is_termination_state" 在声明它受到保护的类之外被使用

#### 121. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:221

- **规则**: `reportAbstractUsage`
- **位置**: 第 221 行, 第 21 列
- **错误信息**: 抽象类 "StateDrivenController" 不可实例化
  未实现 "BaseController.execute"
  未实现 "StateDrivenController._make_decision"

#### 122. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:223

- **规则**: `reportPrivateUsage`
- **位置**: 第 223 行, 第 26 列
- **错误信息**: "_is_termination_state" 在声明它受到保护的类之外被使用

#### 123. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:224

- **规则**: `reportPrivateUsage`
- **位置**: 第 224 行, 第 26 列
- **错误信息**: "_is_termination_state" 在声明它受到保护的类之外被使用

#### 124. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:224

- **规则**: `reportArgumentType`
- **位置**: 第 224 行, 第 48 列
- **错误信息**: "None" 类型的实参无法赋值给函数 "_is_termination_state" 中 "str" 类型的形参 "state"
  "None" 与 "str" 不兼容

#### 125. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:225

- **规则**: `reportPrivateUsage`
- **位置**: 第 225 行, 第 26 列
- **错误信息**: "_is_termination_state" 在声明它受到保护的类之外被使用

#### 126. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:226

- **规则**: `reportPrivateUsage`
- **位置**: 第 226 行, 第 26 列
- **错误信息**: "_is_termination_state" 在声明它受到保护的类之外被使用

#### 127. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:290

- **规则**: `reportUndefinedVariable`
- **位置**: 第 290 行, 第 13 列
- **错误信息**: "patch" 未定义

#### 128. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:292

- **规则**: `reportPrivateUsage`
- **位置**: 第 292 行, 第 23 列
- **错误信息**: "_log_execution" 在声明它受到保护的类之外被使用

#### 129. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:302

- **规则**: `reportAbstractUsage`
- **位置**: 第 302 行, 第 21 列
- **错误信息**: 抽象类 "StateDrivenController" 不可实例化
  未实现 "BaseController.execute"
  未实现 "StateDrivenController._make_decision"

#### 130. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:304

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 304 行, 第 19 列
- **错误信息**: 无法为 "StateDrivenController" 类的 "make_decision" 属性赋值
  属性 "make_decision" 未知

#### 131. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:310

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 310 行, 第 19 列
- **错误信息**: 无法访问 "StateDrivenController" 类的 "make_decision" 属性
  属性 "make_decision" 未知

#### 132. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:316

- **规则**: `reportAbstractUsage`
- **位置**: 第 316 行, 第 21 列
- **错误信息**: 抽象类 "StateDrivenController" 不可实例化
  未实现 "BaseController.execute"
  未实现 "StateDrivenController._make_decision"

#### 133. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:318

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 318 行, 第 19 列
- **错误信息**: 无法为 "StateDrivenController" 类的 "make_decision" 属性赋值
  属性 "make_decision" 未知

#### 134. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:324

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 324 行, 第 19 列
- **错误信息**: 无法访问 "StateDrivenController" 类的 "make_decision" 属性
  属性 "make_decision" 未知

#### 135. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:8

- **规则**: `reportUnusedImport`
- **位置**: 第 8 行, 第 7 列
- **错误信息**: "logging" 导入项未使用

#### 136. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:9

- **规则**: `reportUnusedImport`
- **位置**: 第 9 行, 第 7 列
- **错误信息**: "re" 导入项未使用

#### 137. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:10

- **规则**: `reportUnusedImport`
- **位置**: 第 10 行, 第 20 列
- **错误信息**: "Path" 导入项未使用

#### 138. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:11

- **规则**: `reportUnusedImport`
- **位置**: 第 11 行, 第 39 列
- **错误信息**: "MagicMock" 导入项未使用

#### 139. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:11

- **规则**: `reportUnusedImport`
- **位置**: 第 11 行, 第 50 列
- **错误信息**: "mock_open" 导入项未使用

#### 140. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:26

- **规则**: `reportPrivateUsage`
- **位置**: 第 26 行, 第 21 列
- **错误信息**: "_claude_available" 在声明它受到保护的类之外被使用

#### 141. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:27

- **规则**: `reportPrivateUsage`
- **位置**: 第 27 行, 第 21 列
- **错误信息**: "_current_story_path" 在声明它受到保护的类之外被使用

#### 142. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:35

- **规则**: `reportPrivateUsage`
- **位置**: 第 35 行, 第 21 列
- **错误信息**: "_claude_available" 在声明它受到保护的类之外被使用

#### 143. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:47

- **规则**: `reportPrivateUsage`
- **位置**: 第 47 行, 第 21 列
- **错误信息**: "_log_manager" 在声明它受到保护的类之外被使用

#### 144. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:50

- **规则**: `reportUnknownParameterType`
- **位置**: 第 50 行, 第 60 列
- **错误信息**: "mock_path" 参数的类型未知

#### 145. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:50

- **规则**: `reportMissingParameterType`
- **位置**: 第 50 行, 第 60 列
- **错误信息**: "mock_path" 参数缺少类型注解

#### 146. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:57

- **规则**: `reportPrivateUsage`
- **位置**: 第 57 行, 第 21 列
- **错误信息**: "_claude_available" 在声明它受到保护的类之外被使用

#### 147. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:60

- **规则**: `reportUnknownParameterType`
- **位置**: 第 60 行, 第 54 列
- **错误信息**: "mock_path" 参数的类型未知

#### 148. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:60

- **规则**: `reportMissingParameterType`
- **位置**: 第 60 行, 第 54 列
- **错误信息**: "mock_path" 参数缺少类型注解

#### 149. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:68

- **规则**: `reportPrivateUsage`
- **位置**: 第 68 行, 第 25 列
- **错误信息**: "_claude_available" 在声明它受到保护的类之外被使用

#### 150. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:180

- **规则**: `reportPrivateUsage`
- **位置**: 第 180 行, 第 29 列
- **错误信息**: "_extract_requirements" 在声明它受到保护的类之外被使用

#### 151. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:182

- **规则**: `reportIndexIssue`
- **位置**: 第 182 行, 第 15 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 152. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:183

- **规则**: `reportIndexIssue`
- **位置**: 第 183 行, 第 19 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 153. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:183

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 183 行, 第 19 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 154. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:184

- **规则**: `reportIndexIssue`
- **位置**: 第 184 行, 第 38 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 155. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:185

- **规则**: `reportIndexIssue`
- **位置**: 第 185 行, 第 19 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 156. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:185

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 185 行, 第 19 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 157. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:186

- **规则**: `reportIndexIssue`
- **位置**: 第 186 行, 第 30 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 158. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:187

- **规则**: `reportIndexIssue`
- **位置**: 第 187 行, 第 28 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 159. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:203

- **规则**: `reportPrivateUsage`
- **位置**: 第 203 行, 第 29 列
- **错误信息**: "_extract_requirements" 在声明它受到保护的类之外被使用

#### 160. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:205

- **规则**: `reportIndexIssue`
- **位置**: 第 205 行, 第 15 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 161. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:206

- **规则**: `reportIndexIssue`
- **位置**: 第 206 行, 第 19 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 162. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:206

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 206 行, 第 19 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 163. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:207

- **规则**: `reportIndexIssue`
- **位置**: 第 207 行, 第 37 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 164. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:220

- **规则**: `reportPrivateUsage`
- **位置**: 第 220 行, 第 29 列
- **错误信息**: "_extract_requirements" 在声明它受到保护的类之外被使用

#### 165. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:222

- **规则**: `reportIndexIssue`
- **位置**: 第 222 行, 第 15 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 166. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:223

- **规则**: `reportIndexIssue`
- **位置**: 第 223 行, 第 19 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 167. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:223

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 223 行, 第 19 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 168. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:224

- **规则**: `reportIndexIssue`
- **位置**: 第 224 行, 第 33 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 169. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:225

- **规则**: `reportIndexIssue`
- **位置**: 第 225 行, 第 41 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 170. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:232

- **规则**: `reportPrivateUsage`
- **位置**: 第 232 行, 第 29 列
- **错误信息**: "_extract_requirements" 在声明它受到保护的类之外被使用

#### 171. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:234

- **规则**: `reportIndexIssue`
- **位置**: 第 234 行, 第 15 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 172. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:235

- **规则**: `reportIndexIssue`
- **位置**: 第 235 行, 第 19 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 173. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:235

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 235 行, 第 19 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 174. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:236

- **规则**: `reportIndexIssue`
- **位置**: 第 236 行, 第 19 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 175. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:236

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 236 行, 第 19 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 176. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:237

- **规则**: `reportIndexIssue`
- **位置**: 第 237 行, 第 19 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 177. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:237

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 237 行, 第 19 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 178. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:244

- **规则**: `reportPrivateUsage`
- **位置**: 第 244 行, 第 29 列
- **错误信息**: "_extract_requirements" 在声明它受到保护的类之外被使用

#### 179. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:246

- **规则**: `reportIndexIssue`
- **位置**: 第 246 行, 第 15 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 180. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:247

- **规则**: `reportIndexIssue`
- **位置**: 第 247 行, 第 19 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 181. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:247

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 247 行, 第 19 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 182. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:258

- **规则**: `reportPrivateUsage`
- **位置**: 第 258 行, 第 29 列
- **错误信息**: "_extract_requirements" 在声明它受到保护的类之外被使用

#### 183. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:260

- **规则**: `reportOperatorIssue`
- **位置**: 第 260 行, 第 15 列
- **错误信息**: "Literal['dev_agent_record']" 与 "CoroutineType[Any, Any, dict[str, Any]]" 类型不支持 "in" 运算符

#### 184. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:261

- **规则**: `reportIndexIssue`
- **位置**: 第 261 行, 第 50 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 185. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:268

- **规则**: `reportPrivateUsage`
- **位置**: 第 268 行, 第 33 列
- **错误信息**: "_extract_requirements" 在声明它受到保护的类之外被使用

#### 186. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:282

- **规则**: `reportPrivateUsage`
- **位置**: 第 282 行, 第 37 列
- **错误信息**: "_execute_development_tasks" 在声明它受到保护的类之外被使用

#### 187. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:296

- **规则**: `reportPrivateUsage`
- **位置**: 第 296 行, 第 37 列
- **错误信息**: "_execute_development_tasks" 在声明它受到保护的类之外被使用

#### 188. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:311

- **规则**: `reportPrivateUsage`
- **位置**: 第 311 行, 第 23 列
- **错误信息**: "_validate_prompt_format" 在声明它受到保护的类之外被使用

#### 189. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:321

- **规则**: `reportPrivateUsage`
- **位置**: 第 321 行, 第 27 列
- **错误信息**: "_validate_prompt_format" 在声明它受到保护的类之外被使用

#### 190. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:332

- **规则**: `reportUnusedVariable`
- **位置**: 第 332 行, 第 12 列
- **错误信息**: 变量 "result" 未使用

#### 191. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:332

- **规则**: `reportPrivateUsage`
- **位置**: 第 332 行, 第 27 列
- **错误信息**: "_validate_prompt_format" 在声明它受到保护的类之外被使用

#### 192. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:348

- **规则**: `reportPrivateUsage`
- **位置**: 第 348 行, 第 31 列
- **错误信息**: "_validate_prompt_format" 在声明它受到保护的类之外被使用

#### 193. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:362

- **规则**: `reportPrivateUsage`
- **位置**: 第 362 行, 第 31 列
- **错误信息**: "_validate_prompt_format" 在声明它受到保护的类之外被使用

#### 194. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:376

- **规则**: `reportPrivateUsage`
- **位置**: 第 376 行, 第 31 列
- **错误信息**: "_validate_prompt_format" 在声明它受到保护的类之外被使用

#### 195. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:387

- **规则**: `reportPrivateUsage`
- **位置**: 第 387 行, 第 27 列
- **错误信息**: "_validate_prompt_format" 在声明它受到保护的类之外被使用

#### 196. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:401

- **规则**: `reportPrivateUsage`
- **位置**: 第 401 行, 第 18 列
- **错误信息**: "_log_execution" 在声明它受到保护的类之外被使用

#### 197. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:410

- **规则**: `reportPrivateUsage`
- **位置**: 第 410 行, 第 18 列
- **错误信息**: "_log_execution" 在声明它受到保护的类之外被使用

#### 198. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:419

- **规则**: `reportPrivateUsage`
- **位置**: 第 419 行, 第 18 列
- **错误信息**: "_log_execution" 在声明它受到保护的类之外被使用

#### 199. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:505

- **规则**: `reportPrivateUsage`
- **位置**: 第 505 行, 第 29 列
- **错误信息**: "_extract_requirements" 在声明它受到保护的类之外被使用

#### 200. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:507

- **规则**: `reportIndexIssue`
- **位置**: 第 507 行, 第 28 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 201. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:508

- **规则**: `reportIndexIssue`
- **位置**: 第 508 行, 第 19 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 202. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:508

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 508 行, 第 19 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 203. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:523

- **规则**: `reportPrivateUsage`
- **位置**: 第 523 行, 第 29 列
- **错误信息**: "_extract_requirements" 在声明它受到保护的类之外被使用

#### 204. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:525

- **规则**: `reportIndexIssue`
- **位置**: 第 525 行, 第 19 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 205. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:525

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 525 行, 第 19 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 206. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:526

- **规则**: `reportIndexIssue`
- **位置**: 第 526 行, 第 31 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 207. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:541

- **规则**: `reportPrivateUsage`
- **位置**: 第 541 行, 第 29 列
- **错误信息**: "_extract_requirements" 在声明它受到保护的类之外被使用

#### 208. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:543

- **规则**: `reportIndexIssue`
- **位置**: 第 543 行, 第 19 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 209. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:543

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 543 行, 第 19 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 210. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:544

- **规则**: `reportIndexIssue`
- **位置**: 第 544 行, 第 29 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 211. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:545

- **规则**: `reportIndexIssue`
- **位置**: 第 545 行, 第 27 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 212. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:572

- **规则**: `reportPrivateUsage`
- **位置**: 第 572 行, 第 29 列
- **错误信息**: "_extract_requirements" 在声明它受到保护的类之外被使用

#### 213. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:574

- **规则**: `reportIndexIssue`
- **位置**: 第 574 行, 第 19 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 214. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:574

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 574 行, 第 19 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

#### 215. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:575

- **规则**: `reportIndexIssue`
- **位置**: 第 575 行, 第 35 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 216. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:576

- **规则**: `reportIndexIssue`
- **位置**: 第 576 行, 第 36 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 217. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:577

- **规则**: `reportIndexIssue`
- **位置**: 第 577 行, 第 33 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 218. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:578

- **规则**: `reportIndexIssue`
- **位置**: 第 578 行, 第 19 列
- **错误信息**: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法

#### 219. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:578

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 578 行, 第 19 列
- **错误信息**: 参数类型未知
  实参对应于 "len" 函数中的 "obj" 形参

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\agents\__init__.py`
3. `..\autoBMAD\epic_automation\agents\base_agent.py`
4. `..\autoBMAD\epic_automation\agents\config.py`
5. `..\autoBMAD\epic_automation\agents\dev_agent.py`
6. `..\autoBMAD\epic_automation\agents\pytest_batch_executor.py`
7. `..\autoBMAD\epic_automation\agents\qa_agent.py`
8. `..\autoBMAD\epic_automation\agents\quality_agents.py`
9. `..\autoBMAD\epic_automation\agents\sdk_helper.py`
10. `..\autoBMAD\epic_automation\agents\sm_agent.py`
11. `..\autoBMAD\epic_automation\agents\state_agent.py`
12. `..\autoBMAD\epic_automation\agents\status_update_agent.py`
13. `..\autoBMAD\epic_automation\agents\status_update_agent_old.py`
14. `..\autoBMAD\epic_automation\base_agent.py`
15. `..\autoBMAD\epic_automation\controllers\__init__.py`
16. `..\autoBMAD\epic_automation\controllers\base_controller.py`
17. `..\autoBMAD\epic_automation\controllers\devqa_controller.py`
18. `..\autoBMAD\epic_automation\controllers\quality_controller.py`
19. `..\autoBMAD\epic_automation\controllers\sm_controller.py`
20. `..\autoBMAD\epic_automation\core\__init__.py`
21. `..\autoBMAD\epic_automation\core\cancellation_manager.py`
22. `..\autoBMAD\epic_automation\core\sdk_executor.py`
23. `..\autoBMAD\epic_automation\core\sdk_result.py`
24. `..\autoBMAD\epic_automation\dev_agent.py`
25. `..\autoBMAD\epic_automation\doc_parser.py`
26. `..\autoBMAD\epic_automation\epic_driver.py`
27. `..\autoBMAD\epic_automation\init_db.py`
28. `..\autoBMAD\epic_automation\log_manager.py`
29. `..\autoBMAD\epic_automation\monitoring\__init__.py`
30. `..\autoBMAD\epic_automation\monitoring\resource_monitor.py`
31. `..\autoBMAD\epic_automation\qa_agent.py`
32. `..\autoBMAD\epic_automation\quality_agents.py`
33. `..\autoBMAD\epic_automation\sdk_wrapper.py`
34. `..\autoBMAD\epic_automation\sm_agent.py`
35. `..\autoBMAD\epic_automation\spec_state_manager.py`
36. `..\autoBMAD\epic_automation\state_agent.py`
37. `..\autoBMAD\epic_automation\state_manager.py`
38. `..\autoBMAD\epic_automation\test_automation_agent.py`
39. `..\autoBMAD\epic_automation\tests\test_base_agent.py`
40. `..\autoBMAD\epic_automation\tests\test_controllers.py`
41. `..\autoBMAD\epic_automation\tests\test_dev_agent.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\__init__.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\__init__.py:7:21 - error: "quality_agents" 导入项未使用 (reportUnusedImport)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:7:8 - error: "os" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:12:22 - error: "abstractmethod" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:20:12 - error: "anthropic" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:113:35 - error: `None` 没有 "model" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:114:40 - error: `None` 没有 "max_tokens" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:115:41 - error: `None` 没有 "temperature" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:122:49 - error: 无法访问 "ThinkingBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:122:49 - error: 无法访问 "RedactedThinkingBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:122:49 - error: 无法访问 "ToolUseBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:122:49 - error: 无法访问 "ServerToolUseBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:122:49 - error: 无法访问 "WebSearchToolResultBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:124:38 - error: `None` 没有 "model" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:130:38 - error: `None` 没有 "model" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:153:24 - error: "exc_type" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:153:24 - error: "exc_type" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:153:34 - error: "exc_val" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:153:34 - error: "exc_val" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:153:43 - error: "exc_tb" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:153:43 - error: "exc_tb" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:156:25 - error: `None` 没有 "close" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:215:25 - error: 无法访问 "BrokenWorkerInterpreter" 类的 "started" 属性
    属性 "started" 未知 (reportAttributeAccessIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\config.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\config.py:99:9 - error: "suggestions" 参数的类型部分未知
    参数为 "list[Unknown] | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\config.py:99:31 - error: "list" 泛型类应有类型参数 (reportMissingTypeArgument)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:108:25 - error: "int | bool | str" 类型的实参无法赋值给函数 "__init__" 中 "int" 类型的形参 "timeout"
    "int | bool | str" 类型与 "int" 类型不兼容
      "str" 与 "int" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:109:26 - error: "int | bool | str" 类型的实参无法赋值给函数 "__init__" 中 "bool" 类型的形参 "parallel"
    "int | bool | str" 类型与 "bool" 类型不兼容
      "int" 与 "bool" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:111:26 - error: "int | bool | str" 类型的实参无法赋值给函数 "__init__" 中 "bool" 类型的形参 "blocking"
    "int | bool | str" 类型与 "bool" 类型不兼容
      "int" 与 "bool" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:112:26 - error: "int | bool | str" 类型的实参无法赋值给函数 "__init__" 中 "int" 类型的形参 "priority"
    "int | bool | str" 类型与 "int" 类型不兼容
      "str" 与 "int" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:120:33 - error: "b" 参数的类型未知 (reportUnknownLambdaType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:120:36 - error: 该 `lambda` 的返回类型未知 (reportUnknownLambdaType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:122:61 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:187:29 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:264:16 - error: "asyncio" 可能未绑定 (reportPossiblyUnboundVariable)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\quality_agents.py:8:8 - error: "json" 导入项未使用 (reportUnusedImport)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:890:59 - error: 部分参数的类型未知
    实参对应于 "join" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:901:51 - error: 部分参数的类型未知
    实参对应于 "join" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent.py:14:49 - error: "Optional" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent.py:290:30 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent.py:295:35 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent_old.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent_old.py:62:26 - error: "name" 参数不存在 (reportCallIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\base_controller.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\controllers\base_controller.py:7:8 - error: "asyncio" 导入项未使用 (reportUnusedImport)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\doc_parser.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\doc_parser.py:7:37 - error: "Optional" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\doc_parser.py:56:59 - error: 部分参数的类型未知
    实参对应于 "join" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\doc_parser.py:63:51 - error: 部分参数的类型未知
    实参对应于 "join" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:352:20 - error: "subprocess" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:398:28 - error: "PytestAgent" 未定义 (reportUndefinedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:440:43 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:764:21 - error: 变量 "placeholders" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:983:58 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:1048:22 - error: 变量 "version" 未使用 (reportUnusedVariable)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:8:8 - error: "asyncio" 导入项未使用 (reportUnusedImport)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:11:40 - error: "MagicMock" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:21:24 - error: "config_or_name" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:21:45 - error: "task_group" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:21:62 - error: "log_manager" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:26:15 - error: 返回类型 "dict[Unknown, Unknown]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:26:57 - error: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:185:22 - error: "_log_manager" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:211:45 - error: "mock_anthropic" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:211:45 - error: "mock_anthropic" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:223:48 - error: "mock_anthropic" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:223:48 - error: "mock_anthropic" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:232:52 - error: "mock_anthropic" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:232:52 - error: "mock_anthropic" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:266:51 - error: "mock_read_text" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:266:51 - error: "mock_read_text" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:266:67 - error: "mock_exists" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:266:67 - error: "mock_exists" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:274:9 - error: 变量 "expected_path" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:281:55 - error: "mock_read_text" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:281:55 - error: "mock_read_text" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:281:71 - error: "mock_exists" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:281:71 - error: "mock_exists" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:292:55 - error: "mock_exists" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:292:55 - error: "mock_exists" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:343:20 - error: "MockAgent" 类型的对象不能用于 `async with` 语句，因为它未实现 "__aenter__"
    属性 "__aenter__" 未知 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:343:20 - error: "MockAgent" 类型的对象不能用于 `with` 语句，因为它未实现 "__aexit__"
    属性 "__aexit__" 未知 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:351:20 - error: "MockAgent" 类型的对象不能用于 `async with` 语句，因为它未实现 "__aenter__"
    属性 "__aenter__" 未知 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:351:20 - error: "MockAgent" 类型的对象不能用于 `with` 语句，因为它未实现 "__aexit__"
    属性 "__aexit__" 未知 (reportGeneralTypeIssues)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:382:25 - error: 参数类型未知
    实参对应于 "callable" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:382:31 - error: 无法访问 "MockAgent" 类的 "exit" 属性
    属性 "exit" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:389:19 - error: 无法访问 "MockAgent" 类的 "exit" 属性
    属性 "exit" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:408:33 - error: "_execution_context" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:450:9 - error: 变量 "result1" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:451:9 - error: 变量 "result2" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:467:23 - error: 返回类型 "dict[Unknown, Unknown]" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:467:65 - error: "dict" 泛型类应有类型参数 (reportMissingTypeArgument)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_base_agent.py:478:27 - error: "Literal[123]" 类型的实参无法赋值给函数 "__init__" 中 "AgentConfig | str | None" 类型的形参 "config_or_name"
    "Literal[123]" 类型与 "AgentConfig | str | None" 类型不兼容
      "Literal[123]" 与 "AgentConfig" 不兼容
      "Literal[123]" 与 "str" 不兼容
      "Literal[123]" 与 "None" 不兼容 (reportArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:22:30 - error: "args" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:22:38 - error: "kwargs" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:43:37 - error: "None" 类型的实参无法赋值给函数 "__init__" 中 "TaskGroup" 类型的形参 "task_group"
    "None" 与 "TaskGroup" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:63:35 - error: "_execute_within_taskgroup" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:77:35 - error: "_execute_within_taskgroup" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:84:37 - error: "None" 类型的实参无法赋值给函数 "__init__" 中 "TaskGroup" 类型的形参 "task_group"
    "None" 与 "TaskGroup" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:90:30 - error: "_execute_within_taskgroup" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:97:14 - error: "patch" 未定义 (reportUndefinedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:98:24 - error: "_log_execution" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:107:14 - error: "patch" 未定义 (reportUndefinedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:108:24 - error: "_log_execution" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:117:14 - error: "patch" 未定义 (reportUndefinedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:118:24 - error: "_log_execution" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:127:14 - error: "patch" 未定义 (reportUndefinedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:128:24 - error: "_log_execution" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:139:22 - error: 抽象类 "StateDrivenController" 不可实例化
    未实现 "BaseController.execute"
    未实现 "StateDrivenController._make_decision" (reportAbstractUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:147:22 - error: 抽象类 "StateDrivenController" 不可实例化
    未实现 "BaseController.execute"
    未实现 "StateDrivenController._make_decision" (reportAbstractUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:156:22 - error: 抽象类 "StateDrivenController" 不可实例化
    未实现 "BaseController.execute"
    未实现 "StateDrivenController._make_decision" (reportAbstractUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:159:20 - error: 无法为 "StateDrivenController" 类的 "make_decision" 属性赋值
    属性 "make_decision" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:169:22 - error: 抽象类 "StateDrivenController" 不可实例化
    未实现 "BaseController.execute"
    未实现 "StateDrivenController._make_decision" (reportAbstractUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:172:20 - error: 无法为 "StateDrivenController" 类的 "make_decision" 属性赋值
    属性 "make_decision" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:178:27 - error: 无法访问 "StateDrivenController" 类的 "make_decision" 属性
    属性 "make_decision" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:184:22 - error: 抽象类 "StateDrivenController" 不可实例化
    未实现 "BaseController.execute"
    未实现 "StateDrivenController._make_decision" (reportAbstractUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:187:20 - error: 无法为 "StateDrivenController" 类的 "make_decision" 属性赋值
    属性 "make_decision" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:192:20 - error: 无法访问 "StateDrivenController" 类的 "make_decision" 属性
    属性 "make_decision" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:198:22 - error: 抽象类 "StateDrivenController" 不可实例化
    未实现 "BaseController.execute"
    未实现 "StateDrivenController._make_decision" (reportAbstractUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:201:20 - error: 无法为 "StateDrivenController" 类的 "make_decision" 属性赋值
    属性 "make_decision" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:211:22 - error: 抽象类 "StateDrivenController" 不可实例化
    未实现 "BaseController.execute"
    未实现 "StateDrivenController._make_decision" (reportAbstractUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:213:27 - error: "_is_termination_state" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:214:27 - error: "_is_termination_state" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:215:27 - error: "_is_termination_state" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:216:27 - error: "_is_termination_state" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:221:22 - error: 抽象类 "StateDrivenController" 不可实例化
    未实现 "BaseController.execute"
    未实现 "StateDrivenController._make_decision" (reportAbstractUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:223:27 - error: "_is_termination_state" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:224:27 - error: "_is_termination_state" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:224:49 - error: "None" 类型的实参无法赋值给函数 "_is_termination_state" 中 "str" 类型的形参 "state"
    "None" 与 "str" 不兼容 (reportArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:225:27 - error: "_is_termination_state" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:226:27 - error: "_is_termination_state" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:290:14 - error: "patch" 未定义 (reportUndefinedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:292:24 - error: "_log_execution" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:302:22 - error: 抽象类 "StateDrivenController" 不可实例化
    未实现 "BaseController.execute"
    未实现 "StateDrivenController._make_decision" (reportAbstractUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:304:20 - error: 无法为 "StateDrivenController" 类的 "make_decision" 属性赋值
    属性 "make_decision" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:310:20 - error: 无法访问 "StateDrivenController" 类的 "make_decision" 属性
    属性 "make_decision" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:316:22 - error: 抽象类 "StateDrivenController" 不可实例化
    未实现 "BaseController.execute"
    未实现 "StateDrivenController._make_decision" (reportAbstractUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:318:20 - error: 无法为 "StateDrivenController" 类的 "make_decision" 属性赋值
    属性 "make_decision" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_controllers.py:324:20 - error: 无法访问 "StateDrivenController" 类的 "make_decision" 属性
    属性 "make_decision" 未知 (reportAttributeAccessIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:8:8 - error: "logging" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:9:8 - error: "re" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:10:21 - error: "Path" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:11:40 - error: "MagicMock" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:11:51 - error: "mock_open" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:26:22 - error: "_claude_available" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:27:22 - error: "_current_story_path" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:35:22 - error: "_claude_available" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:47:22 - error: "_log_manager" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:50:61 - error: "mock_path" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:50:61 - error: "mock_path" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:57:22 - error: "_claude_available" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:60:55 - error: "mock_path" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:60:55 - error: "mock_path" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:68:26 - error: "_claude_available" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:180:30 - error: "_extract_requirements" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:182:16 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:183:20 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:183:20 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:184:39 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:185:20 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:185:20 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:186:31 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:187:29 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:203:30 - error: "_extract_requirements" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:205:16 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:206:20 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:206:20 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:207:38 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:220:30 - error: "_extract_requirements" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:222:16 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:223:20 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:223:20 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:224:34 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:225:42 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:232:30 - error: "_extract_requirements" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:234:16 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:235:20 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:235:20 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:236:20 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:236:20 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:237:20 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:237:20 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:244:30 - error: "_extract_requirements" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:246:16 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:247:20 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:247:20 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:258:30 - error: "_extract_requirements" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:260:16 - error: "Literal['dev_agent_record']" 与 "CoroutineType[Any, Any, dict[str, Any]]" 类型不支持 "in" 运算符 (reportOperatorIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:261:51 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:268:34 - error: "_extract_requirements" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:282:38 - error: "_execute_development_tasks" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:296:38 - error: "_execute_development_tasks" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:311:24 - error: "_validate_prompt_format" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:321:28 - error: "_validate_prompt_format" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:332:13 - error: 变量 "result" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:332:28 - error: "_validate_prompt_format" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:348:32 - error: "_validate_prompt_format" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:362:32 - error: "_validate_prompt_format" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:376:32 - error: "_validate_prompt_format" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:387:28 - error: "_validate_prompt_format" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:401:19 - error: "_log_execution" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:410:19 - error: "_log_execution" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:419:19 - error: "_log_execution" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:505:30 - error: "_extract_requirements" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:507:29 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:508:20 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:508:20 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:523:30 - error: "_extract_requirements" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:525:20 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:525:20 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:526:32 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:541:30 - error: "_extract_requirements" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:543:20 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:543:20 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:544:30 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:545:28 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:572:30 - error: "_extract_requirements" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:574:20 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:574:20 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:575:36 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:576:37 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:577:34 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:578:20 - error: "CoroutineType[Any, Any, dict[str, Any]]" 类型上未定义 "__getitem__" 方法 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_dev_agent.py:578:20 - error: 参数类型未知
    实参对应于 "len" 函数中的 "obj" 形参 (reportUnknownArgumentType)
219 errors, 0 warnings, 0 notes
```


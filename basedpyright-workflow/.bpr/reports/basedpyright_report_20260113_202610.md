# BasedPyright 检查报告
**生成时间**: 2026-01-13 20:26:10
**检查时间**: 2026-01-13T20:26:10.740569
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 38 |
| ❌ 错误 (Error) | 51 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.18 秒 |

## 🔴 错误详情

共发现 **51** 个错误

### 按文件分组

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

- `reportUnusedImport`: 10 次
- `reportUnknownArgumentType`: 10 次
- `reportOptionalMemberAccess`: 6 次
- `reportAttributeAccessIssue`: 6 次
- `reportUnknownParameterType`: 4 次
- `reportArgumentType`: 4 次
- `reportMissingParameterType`: 3 次
- `reportUnknownLambdaType`: 2 次
- `reportUnusedVariable`: 2 次
- `reportMissingTypeArgument`: 1 次
- `reportPossiblyUnboundVariable`: 1 次
- `reportCallIssue`: 1 次
- `reportUndefinedVariable`: 1 次

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
51 errors, 0 warnings, 0 notes
```


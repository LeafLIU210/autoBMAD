# BasedPyright 检查报告
**生成时间**: 2026-01-06 07:12:51
**检查时间**: 2026-01-06T07:12:51.551096
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 12 |
| ❌ 错误 (Error) | 64 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.94 秒 |

## 🔴 错误详情

共发现 **64** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py`: 64 个错误

### 按规则分组

- `reportUnknownMemberType`: 19 次
- `reportAttributeAccessIssue`: 19 次
- `reportCallIssue`: 12 次
- `reportUnknownParameterType`: 5 次
- `reportMissingParameterType`: 4 次
- `reportUnknownVariableType`: 4 次
- `reportUnusedImport`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:11

- **规则**: `reportUnusedImport`
- **位置**: 第 11 行, 第 7 列
- **错误信息**: "tempfile" 导入项未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:123

- **规则**: `reportUnknownMemberType`
- **位置**: 第 123 行, 第 24 列
- **错误信息**: "text" 的类型部分未知
  "text" 为 "str | Unknown" 类型

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:123

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 123 行, 第 44 列
- **错误信息**: 无法访问 "ThinkingBlock" 类的 "text" 属性
  属性 "text" 未知

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:123

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 123 行, 第 44 列
- **错误信息**: 无法访问 "RedactedThinkingBlock" 类的 "text" 属性
  属性 "text" 未知

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:123

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 123 行, 第 44 列
- **错误信息**: 无法访问 "ToolUseBlock" 类的 "text" 属性
  属性 "text" 未知

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:123

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 123 行, 第 44 列
- **错误信息**: 无法访问 "ServerToolUseBlock" 类的 "text" 属性
  属性 "text" 未知

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:123

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 123 行, 第 44 列
- **错误信息**: 无法访问 "WebSearchToolResultBlock" 类的 "text" 属性
  属性 "text" 未知

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:147

- **规则**: `reportUnknownParameterType`
- **位置**: 第 147 行, 第 23 列
- **错误信息**: "exc_type" 参数的类型未知

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:147

- **规则**: `reportMissingParameterType`
- **位置**: 第 147 行, 第 23 列
- **错误信息**: "exc_type" 参数缺少类型注解

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:147

- **规则**: `reportUnknownParameterType`
- **位置**: 第 147 行, 第 33 列
- **错误信息**: "exc_val" 参数的类型未知

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:147

- **规则**: `reportMissingParameterType`
- **位置**: 第 147 行, 第 33 列
- **错误信息**: "exc_val" 参数缺少类型注解

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:147

- **规则**: `reportUnknownParameterType`
- **位置**: 第 147 行, 第 42 列
- **错误信息**: "exc_tb" 参数的类型未知

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:147

- **规则**: `reportMissingParameterType`
- **位置**: 第 147 行, 第 42 列
- **错误信息**: "exc_tb" 参数缺少类型注解

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:280

- **规则**: `reportUnknownParameterType`
- **位置**: 第 280 行, 第 8 列
- **错误信息**: 返回类型 "str | Unknown" 部分未知

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:282

- **规则**: `reportUnknownMemberType`
- **位置**: 第 282 行, 第 15 列
- **错误信息**: "gate" 的类型部分未知
  "gate" 为 "str | Unknown" 类型

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:282

- **规则**: `reportUnknownVariableType`
- **位置**: 第 282 行, 第 15 列
- **错误信息**: 返回类型 "str | Unknown" 部分未知

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:285

- **规则**: `reportUnknownParameterType`
- **位置**: 第 285 行, 第 21 列
- **错误信息**: "value" 参数的类型未知

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:285

- **规则**: `reportMissingParameterType`
- **位置**: 第 285 行, 第 21 列
- **错误信息**: "value" 参数缺少类型注解

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:287

- **规则**: `reportUnknownMemberType`
- **位置**: 第 287 行, 第 8 列
- **错误信息**: "gate" 类型未知

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:353

- **规则**: `reportUnknownVariableType`
- **位置**: 第 353 行, 第 8 列
- **错误信息**: "implementation" 的类型部分未知
  "implementation" 为 "str | Unknown" 类型

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:353

- **规则**: `reportUnknownMemberType`
- **位置**: 第 353 行, 第 25 列
- **错误信息**: "text" 的类型部分未知
  "text" 为 "str | Unknown" 类型

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:353

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 353 行, 第 45 列
- **错误信息**: 无法访问 "ThinkingBlock" 类的 "text" 属性
  属性 "text" 未知

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:353

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 353 行, 第 45 列
- **错误信息**: 无法访问 "RedactedThinkingBlock" 类的 "text" 属性
  属性 "text" 未知

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:353

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 353 行, 第 45 列
- **错误信息**: 无法访问 "ToolUseBlock" 类的 "text" 属性
  属性 "text" 未知

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:353

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 353 行, 第 45 列
- **错误信息**: 无法访问 "ServerToolUseBlock" 类的 "text" 属性
  属性 "text" 未知

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:353

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 353 行, 第 45 列
- **错误信息**: 无法访问 "WebSearchToolResultBlock" 类的 "text" 属性
  属性 "text" 未知

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:399

- **规则**: `reportUnknownVariableType`
- **位置**: 第 399 行, 第 8 列
- **错误信息**: "tests" 的类型部分未知
  "tests" 为 "str | Unknown" 类型

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:399

- **规则**: `reportUnknownMemberType`
- **位置**: 第 399 行, 第 16 列
- **错误信息**: "text" 的类型部分未知
  "text" 为 "str | Unknown" 类型

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:399

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 399 行, 第 36 列
- **错误信息**: 无法访问 "ThinkingBlock" 类的 "text" 属性
  属性 "text" 未知

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:399

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 399 行, 第 36 列
- **错误信息**: 无法访问 "RedactedThinkingBlock" 类的 "text" 属性
  属性 "text" 未知

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:399

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 399 行, 第 36 列
- **错误信息**: 无法访问 "ToolUseBlock" 类的 "text" 属性
  属性 "text" 未知

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:399

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 399 行, 第 36 列
- **错误信息**: 无法访问 "ServerToolUseBlock" 类的 "text" 属性
  属性 "text" 未知

#### 33. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:399

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 399 行, 第 36 列
- **错误信息**: 无法访问 "WebSearchToolResultBlock" 类的 "text" 属性
  属性 "text" 未知

#### 34. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:435

- **规则**: `reportUnknownMemberType`
- **位置**: 第 435 行, 第 16 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 35. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:442

- **规则**: `reportUnknownMemberType`
- **位置**: 第 442 行, 第 16 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 36. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:449

- **规则**: `reportUnknownMemberType`
- **位置**: 第 449 行, 第 16 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 37. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:457

- **规则**: `reportUnknownMemberType`
- **位置**: 第 457 行, 第 26 列
- **错误信息**: "run_tests" 类型未知

#### 38. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:457

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 457 行, 第 38 列
- **错误信息**: 无法访问 "AgentConfig" 类的 "run_tests" 属性
  属性 "run_tests" 未知

#### 39. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:466

- **规则**: `reportUnknownMemberType`
- **位置**: 第 466 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 40. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:473

- **规则**: `reportUnknownMemberType`
- **位置**: 第 473 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 41. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:480

- **规则**: `reportUnknownMemberType`
- **位置**: 第 480 行, 第 20 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 42. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:553

- **规则**: `reportUnknownMemberType`
- **位置**: 第 553 行, 第 32 列
- **错误信息**: "source_dir" 类型未知

#### 43. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:553

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 553 行, 第 44 列
- **错误信息**: 无法访问 "AgentConfig" 类的 "source_dir" 属性
  属性 "source_dir" 未知

#### 44. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:554

- **规则**: `reportUnknownMemberType`
- **位置**: 第 554 行, 第 30 列
- **错误信息**: "test_dir" 类型未知

#### 45. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:554

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 554 行, 第 42 列
- **错误信息**: 无法访问 "AgentConfig" 类的 "test_dir" 属性
  属性 "test_dir" 未知

#### 46. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:555

- **规则**: `reportUnknownMemberType`
- **位置**: 第 555 行, 第 30 列
- **错误信息**: "test_framework" 类型未知

#### 47. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:555

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 555 行, 第 42 列
- **错误信息**: 无法访问 "AgentConfig" 类的 "test_framework" 属性
  属性 "test_framework" 未知

#### 48. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:591

- **规则**: `reportUnknownMemberType`
- **位置**: 第 591 行, 第 16 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 49. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:591

- **规则**: `reportCallIssue`
- **位置**: 第 591 行, 第 31 列
- **错误信息**: 参数 "gate", "status_reason" 缺少传入值

#### 50. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:592

- **规则**: `reportCallIssue`
- **位置**: 第 592 行, 第 20 列
- **错误信息**: "status" 参数不存在

#### 51. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:593

- **规则**: `reportCallIssue`
- **位置**: 第 593 行, 第 20 列
- **错误信息**: "message" 参数不存在

#### 52. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:596

- **规则**: `reportUnknownMemberType`
- **位置**: 第 596 行, 第 16 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 53. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:596

- **规则**: `reportCallIssue`
- **位置**: 第 596 行, 第 31 列
- **错误信息**: 参数 "gate", "status_reason" 缺少传入值

#### 54. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:597

- **规则**: `reportCallIssue`
- **位置**: 第 597 行, 第 20 列
- **错误信息**: "status" 参数不存在

#### 55. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:598

- **规则**: `reportCallIssue`
- **位置**: 第 598 行, 第 20 列
- **错误信息**: "message" 参数不存在

#### 56. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:604

- **规则**: `reportUnknownMemberType`
- **位置**: 第 604 行, 第 16 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 57. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:604

- **规则**: `reportCallIssue`
- **位置**: 第 604 行, 第 31 列
- **错误信息**: 参数 "gate", "status_reason" 缺少传入值

#### 58. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:605

- **规则**: `reportCallIssue`
- **位置**: 第 605 行, 第 20 列
- **错误信息**: "status" 参数不存在

#### 59. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:606

- **规则**: `reportCallIssue`
- **位置**: 第 606 行, 第 20 列
- **错误信息**: "message" 参数不存在

#### 60. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:609

- **规则**: `reportUnknownMemberType`
- **位置**: 第 609 行, 第 16 列
- **错误信息**: "append" 的类型部分未知
  "append" 为 "(object: Unknown, /) -> None" 类型

#### 61. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:609

- **规则**: `reportCallIssue`
- **位置**: 第 609 行, 第 31 列
- **错误信息**: 参数 "gate", "status_reason" 缺少传入值

#### 62. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:610

- **规则**: `reportCallIssue`
- **位置**: 第 610 行, 第 20 列
- **错误信息**: "status" 参数不存在

#### 63. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:611

- **规则**: `reportCallIssue`
- **位置**: 第 611 行, 第 20 列
- **错误信息**: "message" 参数不存在

#### 64. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:614

- **规则**: `reportUnknownVariableType`
- **位置**: 第 614 行, 第 15 列
- **错误信息**: 返回类型 "list[Unknown]" 部分未知

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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:11:8 - error: "tempfile" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:123:25 - error: "text" 的类型部分未知
    "text" 为 "str | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:123:45 - error: 无法访问 "ThinkingBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:123:45 - error: 无法访问 "RedactedThinkingBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:123:45 - error: 无法访问 "ToolUseBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:123:45 - error: 无法访问 "ServerToolUseBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:123:45 - error: 无法访问 "WebSearchToolResultBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:147:24 - error: "exc_type" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:147:24 - error: "exc_type" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:147:34 - error: "exc_val" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:147:34 - error: "exc_val" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:147:43 - error: "exc_tb" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:147:43 - error: "exc_tb" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:280:9 - error: 返回类型 "str | Unknown" 部分未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:282:16 - error: "gate" 的类型部分未知
    "gate" 为 "str | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:282:16 - error: 返回类型 "str | Unknown" 部分未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:285:22 - error: "value" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:285:22 - error: "value" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:287:9 - error: "gate" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:353:9 - error: "implementation" 的类型部分未知
    "implementation" 为 "str | Unknown" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:353:26 - error: "text" 的类型部分未知
    "text" 为 "str | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:353:46 - error: 无法访问 "ThinkingBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:353:46 - error: 无法访问 "RedactedThinkingBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:353:46 - error: 无法访问 "ToolUseBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:353:46 - error: 无法访问 "ServerToolUseBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:353:46 - error: 无法访问 "WebSearchToolResultBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:399:9 - error: "tests" 的类型部分未知
    "tests" 为 "str | Unknown" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:399:17 - error: "text" 的类型部分未知
    "text" 为 "str | Unknown" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:399:37 - error: 无法访问 "ThinkingBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:399:37 - error: 无法访问 "RedactedThinkingBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:399:37 - error: 无法访问 "ToolUseBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:399:37 - error: 无法访问 "ServerToolUseBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:399:37 - error: 无法访问 "WebSearchToolResultBlock" 类的 "text" 属性
    属性 "text" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:435:17 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:442:17 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:449:17 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:457:27 - error: "run_tests" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:457:39 - error: 无法访问 "AgentConfig" 类的 "run_tests" 属性
    属性 "run_tests" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:466:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:473:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:480:21 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:553:33 - error: "source_dir" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:553:45 - error: 无法访问 "AgentConfig" 类的 "source_dir" 属性
    属性 "source_dir" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:554:31 - error: "test_dir" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:554:43 - error: 无法访问 "AgentConfig" 类的 "test_dir" 属性
    属性 "test_dir" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:555:31 - error: "test_framework" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:555:43 - error: 无法访问 "AgentConfig" 类的 "test_framework" 属性
    属性 "test_framework" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:591:17 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:591:32 - error: 参数 "gate", "status_reason" 缺少传入值 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:592:21 - error: "status" 参数不存在 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:593:21 - error: "message" 参数不存在 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:596:17 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:596:32 - error: 参数 "gate", "status_reason" 缺少传入值 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:597:21 - error: "status" 参数不存在 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:598:21 - error: "message" 参数不存在 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:604:17 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:604:32 - error: 参数 "gate", "status_reason" 缺少传入值 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:605:21 - error: "status" 参数不存在 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:606:21 - error: "message" 参数不存在 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:609:17 - error: "append" 的类型部分未知
    "append" 为 "(object: Unknown, /) -> None" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:609:32 - error: 参数 "gate", "status_reason" 缺少传入值 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:610:21 - error: "status" 参数不存在 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:611:21 - error: "message" 参数不存在 (reportCallIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents.py:614:16 - error: 返回类型 "list[Unknown]" 部分未知 (reportUnknownVariableType)
64 errors, 0 warnings, 0 notes
```


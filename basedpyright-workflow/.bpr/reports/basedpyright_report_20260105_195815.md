# BasedPyright 检查报告
**生成时间**: 2026-01-05 19:58:15
**检查时间**: 2026-01-05T19:58:15.247413
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 10 |
| ❌ 错误 (Error) | 72 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.61 秒 |

## 🔴 错误详情

共发现 **72** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 65 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py`: 4 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py`: 3 个错误

### 按规则分组

- `reportUnknownMemberType`: 23 次
- `reportAttributeAccessIssue`: 18 次
- `reportIndexIssue`: 15 次
- `reportUnknownVariableType`: 11 次
- `reportUnusedVariable`: 2 次
- `reportUnusedImport`: 1 次
- `reportMissingImports`: 1 次
- `reportUnknownParameterType`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:31

- **规则**: `reportIndexIssue`
- **位置**: 第 31 行, 第 13 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:31

- **规则**: `reportIndexIssue`
- **位置**: 第 31 行, 第 18 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:42

- **规则**: `reportIndexIssue`
- **位置**: 第 42 行, 第 19 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:142

- **规则**: `reportIndexIssue`
- **位置**: 第 142 行, 第 34 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:142

- **规则**: `reportIndexIssue`
- **位置**: 第 142 行, 第 39 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:225

- **规则**: `reportUnknownMemberType`
- **位置**: 第 225 行, 第 33 列
- **错误信息**: "create_stories_from_epic" 类型未知

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:225

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 225 行, 第 47 列
- **错误信息**: 无法访问 "object" 类的 "create_stories_from_epic" 属性
  属性 "create_stories_from_epic" 未知

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:264

- **规则**: `reportIndexIssue`
- **位置**: 第 264 行, 第 60 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:334

- **规则**: `reportUnknownVariableType`
- **位置**: 第 334 行, 第 12 列
- **错误信息**: "result" 类型未知

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:334

- **规则**: `reportUnknownMemberType`
- **位置**: 第 334 行, 第 27 列
- **错误信息**: "execute" 类型未知

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:334

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 334 行, 第 41 列
- **错误信息**: 无法访问 "object" 类的 "execute" 属性
  属性 "execute" 未知

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:337

- **规则**: `reportUnknownMemberType`
- **位置**: 第 337 行, 第 18 列
- **错误信息**: "update_story_status" 类型未知

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:337

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 337 行, 第 37 列
- **错误信息**: 无法访问 "object" 类的 "update_story_status" 属性
  属性 "update_story_status" 未知

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:344

- **规则**: `reportUnknownVariableType`
- **位置**: 第 344 行, 第 19 列
- **错误信息**: 返回类型未知

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:348

- **规则**: `reportUnknownMemberType`
- **位置**: 第 348 行, 第 18 列
- **错误信息**: "update_story_status" 类型未知

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:348

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 348 行, 第 37 列
- **错误信息**: 无法访问 "object" 类的 "update_story_status" 属性
  属性 "update_story_status" 未知

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:371

- **规则**: `reportUnknownMemberType`
- **位置**: 第 371 行, 第 18 列
- **错误信息**: "update_story_status" 类型未知

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:371

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 371 行, 第 37 列
- **错误信息**: 无法访问 "object" 类的 "update_story_status" 属性
  属性 "update_story_status" 未知

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:387

- **规则**: `reportUnknownVariableType`
- **位置**: 第 387 行, 第 12 列
- **错误信息**: "result" 类型未知

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:387

- **规则**: `reportUnknownMemberType`
- **位置**: 第 387 行, 第 27 列
- **错误信息**: "execute" 类型未知

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:387

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 387 行, 第 42 列
- **错误信息**: 无法访问 "object" 类的 "execute" 属性
  属性 "execute" 未知

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:390

- **规则**: `reportUnknownMemberType`
- **位置**: 第 390 行, 第 18 列
- **错误信息**: "update_story_status" 类型未知

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:390

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 390 行, 第 37 列
- **错误信息**: 无法访问 "object" 类的 "update_story_status" 属性
  属性 "update_story_status" 未知

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:398

- **规则**: `reportUnknownVariableType`
- **位置**: 第 398 行, 第 19 列
- **错误信息**: 返回类型未知

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:402

- **规则**: `reportUnknownMemberType`
- **位置**: 第 402 行, 第 18 列
- **错误信息**: "update_story_status" 类型未知

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:402

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 402 行, 第 37 列
- **错误信息**: 无法访问 "object" 类的 "update_story_status" 属性
  属性 "update_story_status" 未知

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:425

- **规则**: `reportUnknownMemberType`
- **位置**: 第 425 行, 第 18 列
- **错误信息**: "update_story_status" 类型未知

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:425

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 425 行, 第 37 列
- **错误信息**: 无法访问 "object" 类的 "update_story_status" 属性
  属性 "update_story_status" 未知

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:441

- **规则**: `reportUnknownVariableType`
- **位置**: 第 441 行, 第 12 列
- **错误信息**: "qa_result" 类型未知

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:441

- **规则**: `reportUnknownMemberType`
- **位置**: 第 441 行, 第 30 列
- **错误信息**: "execute" 类型未知

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:441

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 441 行, 第 44 列
- **错误信息**: 无法访问 "object" 类的 "execute" 属性
  属性 "execute" 未知

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:450

- **规则**: `reportUnknownMemberType`
- **位置**: 第 450 行, 第 18 列
- **错误信息**: "update_story_status" 类型未知

#### 33. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:450

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 450 行, 第 37 列
- **错误信息**: 无法访问 "object" 类的 "update_story_status" 属性
  属性 "update_story_status" 未知

#### 34. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:457

- **规则**: `reportUnknownMemberType`
- **位置**: 第 457 行, 第 15 列
- **错误信息**: "get" 类型未知

#### 35. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:459

- **规则**: `reportUnknownMemberType`
- **位置**: 第 459 行, 第 22 列
- **错误信息**: "update_story_status" 类型未知

#### 36. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:459

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 459 行, 第 41 列
- **错误信息**: 无法访问 "object" 类的 "update_story_status" 属性
  属性 "update_story_status" 未知

#### 37. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:470

- **规则**: `reportUnknownMemberType`
- **位置**: 第 470 行, 第 18 列
- **错误信息**: "update_story_status" 类型未知

#### 38. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:470

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 470 行, 第 37 列
- **错误信息**: 无法访问 "object" 类的 "update_story_status" 属性
  属性 "update_story_status" 未知

#### 39. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:477

- **规则**: `reportIndexIssue`
- **位置**: 第 477 行, 第 41 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 40. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:493

- **规则**: `reportUnknownVariableType`
- **位置**: 第 493 行, 第 12 列
- **错误信息**: "existing_status" 类型未知

#### 41. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:493

- **规则**: `reportUnknownMemberType`
- **位置**: 第 493 行, 第 36 列
- **错误信息**: "get_story_status" 类型未知

#### 42. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:493

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 493 行, 第 55 列
- **错误信息**: 无法访问 "object" 类的 "get_story_status" 属性
  属性 "get_story_status" 未知

#### 43. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:494

- **规则**: `reportUnknownMemberType`
- **位置**: 第 494 行, 第 35 列
- **错误信息**: "get" 类型未知

#### 44. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:540

- **规则**: `reportUnknownMemberType`
- **位置**: 第 540 行, 第 18 列
- **错误信息**: "update_story_status" 类型未知

#### 45. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:540

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 540 行, 第 37 列
- **错误信息**: 无法访问 "object" 类的 "update_story_status" 属性
  属性 "update_story_status" 未知

#### 46. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:564

- **规则**: `reportIndexIssue`
- **位置**: 第 564 行, 第 50 列
- **错误信息**: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 47. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:564

- **规则**: `reportIndexIssue`
- **位置**: 第 564 行, 第 55 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 48. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:599

- **规则**: `reportIndexIssue`
- **位置**: 第 599 行, 第 45 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 49. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:617

- **规则**: `reportUnknownVariableType`
- **位置**: 第 617 行, 第 12 列
- **错误信息**: "quality_agent" 类型未知

#### 50. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:623

- **规则**: `reportUnknownVariableType`
- **位置**: 第 623 行, 第 12 列
- **错误信息**: "raw_results" 的类型部分未知
  "raw_results" 为 "Unknown | Any" 类型

#### 51. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:623

- **规则**: `reportUnknownMemberType`
- **位置**: 第 623 行, 第 37 列
- **错误信息**: "run_quality_gates" 的类型部分未知
  "run_quality_gates" 为 "Unknown | Any" 类型

#### 52. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:627

- **规则**: `reportIndexIssue`
- **位置**: 第 627 行, 第 51 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 53. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:647

- **规则**: `reportIndexIssue`
- **位置**: 第 647 行, 第 47 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 54. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:665

- **规则**: `reportUnknownVariableType`
- **位置**: 第 665 行, 第 12 列
- **错误信息**: "test_agent" 类型未知

#### 55. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:671

- **规则**: `reportUnknownVariableType`
- **位置**: 第 671 行, 第 12 列
- **错误信息**: "raw_results" 的类型部分未知
  "raw_results" 为 "Unknown | Any" 类型

#### 56. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:671

- **规则**: `reportUnknownMemberType`
- **位置**: 第 671 行, 第 37 列
- **错误信息**: "run_test_automation" 的类型部分未知
  "run_test_automation" 为 "Unknown | Any" 类型

#### 57. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:675

- **规则**: `reportIndexIssue`
- **位置**: 第 675 行, 第 48 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 58. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:716

- **规则**: `reportIndexIssue`
- **位置**: 第 716 行, 第 71 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 59. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:731

- **规则**: `reportUnknownMemberType`
- **位置**: 第 731 行, 第 22 列
- **错误信息**: "update_epic_status" 类型未知

#### 60. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:731

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 731 行, 第 41 列
- **错误信息**: 无法访问 "object" 类的 "update_epic_status" 属性
  属性 "update_epic_status" 未知

#### 61. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:739

- **规则**: `reportUnknownMemberType`
- **位置**: 第 739 行, 第 22 列
- **错误信息**: "update_epic_status" 类型未知

#### 62. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:739

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 739 行, 第 41 列
- **错误信息**: 无法访问 "object" 类的 "update_epic_status" 属性
  属性 "update_epic_status" 未知

#### 63. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:759

- **规则**: `reportUnknownMemberType`
- **位置**: 第 759 行, 第 18 列
- **错误信息**: "update_epic_status" 类型未知

#### 64. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:759

- **规则**: `reportAttributeAccessIssue`
- **位置**: 第 759 行, 第 37 列
- **错误信息**: 无法访问 "object" 类的 "update_epic_status" 属性
  属性 "update_epic_status" 未知

#### 65. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:772

- **规则**: `reportIndexIssue`
- **位置**: 第 772 行, 第 40 列
- **错误信息**: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式

#### 66. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:17

- **规则**: `reportUnusedImport`
- **位置**: 第 17 行, 第 38 列
- **错误信息**: "QAAutomationWorkflow" 导入项未使用

#### 67. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:90

- **规则**: `reportUnusedVariable`
- **位置**: 第 90 行, 第 12 列
- **错误信息**: 变量 "validations" 未使用

#### 68. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:93

- **规则**: `reportUnusedVariable`
- **位置**: 第 93 行, 第 12 列
- **错误信息**: 变量 "qa_result" 未使用

#### 69. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:13

- **规则**: `reportMissingImports`
- **位置**: 第 13 行, 第 5 列
- **错误信息**: 无法解析导入 "autoBMAD.epic_automation.state_manager"

#### 70. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:13

- **规则**: `reportUnknownVariableType`
- **位置**: 第 13 行, 第 51 列
- **错误信息**: "StateManager" 类型未知

#### 71. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:20

- **规则**: `reportUnknownParameterType`
- **位置**: 第 20 行, 第 23 列
- **错误信息**: "state_manager" 参数的类型未知

#### 72. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21

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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:31:14 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:31:19 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:42:20 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:142:35 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:142:40 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:225:34 - error: "create_stories_from_epic" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:225:48 - error: 无法访问 "object" 类的 "create_stories_from_epic" 属性
    属性 "create_stories_from_epic" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:264:61 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:334:13 - error: "result" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:334:28 - error: "execute" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:334:42 - error: 无法访问 "object" 类的 "execute" 属性
    属性 "execute" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:337:19 - error: "update_story_status" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:337:38 - error: 无法访问 "object" 类的 "update_story_status" 属性
    属性 "update_story_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:344:20 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:348:19 - error: "update_story_status" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:348:38 - error: 无法访问 "object" 类的 "update_story_status" 属性
    属性 "update_story_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:371:19 - error: "update_story_status" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:371:38 - error: 无法访问 "object" 类的 "update_story_status" 属性
    属性 "update_story_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:387:13 - error: "result" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:387:28 - error: "execute" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:387:43 - error: 无法访问 "object" 类的 "execute" 属性
    属性 "execute" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:390:19 - error: "update_story_status" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:390:38 - error: 无法访问 "object" 类的 "update_story_status" 属性
    属性 "update_story_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:398:20 - error: 返回类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:402:19 - error: "update_story_status" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:402:38 - error: 无法访问 "object" 类的 "update_story_status" 属性
    属性 "update_story_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:425:19 - error: "update_story_status" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:425:38 - error: 无法访问 "object" 类的 "update_story_status" 属性
    属性 "update_story_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:441:13 - error: "qa_result" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:441:31 - error: "execute" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:441:45 - error: 无法访问 "object" 类的 "execute" 属性
    属性 "execute" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:450:19 - error: "update_story_status" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:450:38 - error: 无法访问 "object" 类的 "update_story_status" 属性
    属性 "update_story_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:457:16 - error: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:459:23 - error: "update_story_status" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:459:42 - error: 无法访问 "object" 类的 "update_story_status" 属性
    属性 "update_story_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:470:19 - error: "update_story_status" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:470:38 - error: 无法访问 "object" 类的 "update_story_status" 属性
    属性 "update_story_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:477:42 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:493:13 - error: "existing_status" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:493:37 - error: "get_story_status" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:493:56 - error: 无法访问 "object" 类的 "get_story_status" 属性
    属性 "get_story_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:494:36 - error: "get" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:540:19 - error: "update_story_status" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:540:38 - error: 无法访问 "object" 类的 "update_story_status" 属性
    属性 "update_story_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:564:51 - error: 在 "list" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:564:56 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:599:46 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:617:13 - error: "quality_agent" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:623:13 - error: "raw_results" 的类型部分未知
    "raw_results" 为 "Unknown | Any" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:623:38 - error: "run_quality_gates" 的类型部分未知
    "run_quality_gates" 为 "Unknown | Any" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:627:52 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:647:48 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:665:13 - error: "test_agent" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:671:13 - error: "raw_results" 的类型部分未知
    "raw_results" 为 "Unknown | Any" 类型 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:671:38 - error: "run_test_automation" 的类型部分未知
    "run_test_automation" 为 "Unknown | Any" 类型 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:675:49 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:716:72 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:731:23 - error: "update_epic_status" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:731:42 - error: 无法访问 "object" 类的 "update_epic_status" 属性
    属性 "update_epic_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:739:23 - error: "update_epic_status" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:739:42 - error: 无法访问 "object" 类的 "update_epic_status" 属性
    属性 "update_epic_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:759:19 - error: "update_epic_status" 类型未知 (reportUnknownMemberType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:759:38 - error: 无法访问 "object" 类的 "update_epic_status" 属性
    属性 "update_epic_status" 未知 (reportAttributeAccessIssue)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:772:41 - error: 在 "dict" 类上使用的下标将导致运行时异常，应将整个类型表达式写成字符串形式 (reportIndexIssue)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:17:39 - error: "QAAutomationWorkflow" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:90:13 - error: 变量 "validations" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:93:13 - error: 变量 "qa_result" 未使用 (reportUnusedVariable)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:13:6 - error: 无法解析导入 "autoBMAD.epic_automation.state_manager" (reportMissingImports)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:13:52 - error: "StateManager" 类型未知 (reportUnknownVariableType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:20:24 - error: "state_manager" 参数的类型未知 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_automation_agent.py:21:9 - error: "state_manager" 类型未知 (reportUnknownMemberType)
72 errors, 0 warnings, 0 notes
```


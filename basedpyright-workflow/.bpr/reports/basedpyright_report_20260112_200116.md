# BasedPyright 检查报告
**生成时间**: 2026-01-12 20:01:16
**检查时间**: 2026-01-12T20:01:16.705473
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 27 |
| ❌ 错误 (Error) | 39 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 0.91 秒 |

## 🔴 错误详情

共发现 **39** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py`: 32 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py`: 2 个错误

### 按规则分组

- `reportPrivateUsage`: 17 次
- `reportOptionalMemberAccess`: 13 次
- `reportUnusedImport`: 5 次
- `reportReturnType`: 2 次
- `reportInvalidStringEscapeSequence`: 2 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:8

- **规则**: `reportUnusedImport`
- **位置**: 第 8 行, 第 7 列
- **错误信息**: "os" 导入项未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:10

- **规则**: `reportUnusedImport`
- **位置**: 第 10 行, 第 7 列
- **错误信息**: "time" 导入项未使用

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:742

- **规则**: `reportUnusedImport`
- **位置**: 第 742 行, 第 40 列
- **错误信息**: "PathlibPath" 导入项未使用

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1124

- **规则**: `reportReturnType`
- **位置**: 第 1124 行, 第 57 列
- **错误信息**: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
  "None" 与 "bool" 不兼容

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1175

- **规则**: `reportReturnType`
- **位置**: 第 1175 行, 第 78 列
- **错误信息**: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
  "None" 与 "bool" 不兼容

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:732

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 732 行, 第 61 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:732

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 732 行, 第 63 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:5

- **规则**: `reportUnusedImport`
- **位置**: 第 5 行, 第 7 列
- **错误信息**: "anyio" 导入项未使用

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:6

- **规则**: `reportUnusedImport`
- **位置**: 第 6 行, 第 26 列
- **错误信息**: "MagicMock" 导入项未使用

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:65

- **规则**: `reportPrivateUsage`
- **位置**: 第 65 行, 第 23 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:66

- **规则**: `reportPrivateUsage`
- **位置**: 第 66 行, 第 23 列
- **错误信息**: "_lock" 在声明它受到保护的类之外被使用

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:73

- **规则**: `reportPrivateUsage`
- **位置**: 第 73 行, 第 35 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:74

- **规则**: `reportPrivateUsage`
- **位置**: 第 74 行, 第 28 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:87

- **规则**: `reportPrivateUsage`
- **位置**: 第 87 行, 第 27 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:88

- **规则**: `reportPrivateUsage`
- **位置**: 第 88 行, 第 35 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:89

- **规则**: `reportPrivateUsage`
- **位置**: 第 89 行, 第 35 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:90

- **规则**: `reportPrivateUsage`
- **位置**: 第 90 行, 第 35 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:99

- **规则**: `reportPrivateUsage`
- **位置**: 第 99 行, 第 28 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:108

- **规则**: `reportPrivateUsage`
- **位置**: 第 108 行, 第 28 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 20. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:117

- **规则**: `reportPrivateUsage`
- **位置**: 第 117 行, 第 49 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 21. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:125

- **规则**: `reportPrivateUsage`
- **位置**: 第 125 行, 第 28 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 22. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:134

- **规则**: `reportPrivateUsage`
- **位置**: 第 134 行, 第 49 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 23. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:142

- **规则**: `reportPrivateUsage`
- **位置**: 第 142 行, 第 28 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 24. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:151

- **规则**: `reportPrivateUsage`
- **位置**: 第 151 行, 第 49 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 25. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:176

- **规则**: `reportPrivateUsage`
- **位置**: 第 176 行, 第 39 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 26. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:185

- **规则**: `reportPrivateUsage`
- **位置**: 第 185 行, 第 35 列
- **错误信息**: "_active_calls" 在声明它受到保护的类之外被使用

#### 27. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:262

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 262 行, 第 25 列
- **错误信息**: `None` 没有 "cleanup_completed" 属性

#### 28. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:276

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 276 行, 第 25 列
- **错误信息**: `None` 没有 "cleanup_completed" 属性

#### 29. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:288

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 288 行, 第 25 列
- **错误信息**: `None` 没有 "cleanup_completed" 属性

#### 30. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:304

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 304 行, 第 25 列
- **错误信息**: `None` 没有 "cancel_requested" 属性

#### 31. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:309

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 309 行, 第 25 列
- **错误信息**: `None` 没有 "cleanup_completed" 属性

#### 32. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:318

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 318 行, 第 25 列
- **错误信息**: `None` 没有 "has_target_result" 属性

#### 33. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:331

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 331 行, 第 26 列
- **错误信息**: `None` 没有 "agent_name" 属性

#### 34. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:332

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 332 行, 第 26 列
- **错误信息**: `None` 没有 "agent_name" 属性

#### 35. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:333

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 333 行, 第 26 列
- **错误信息**: `None` 没有 "agent_name" 属性

#### 36. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:337

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 337 行, 第 26 列
- **错误信息**: `None` 没有 "cancel_requested" 属性

#### 37. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:338

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 338 行, 第 26 列
- **错误信息**: `None` 没有 "cancel_requested" 属性

#### 38. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:339

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 339 行, 第 26 列
- **错误信息**: `None` 没有 "cancel_requested" 属性

#### 39. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:353

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 353 行, 第 27 列
- **错误信息**: `None` 没有 "agent_name" 属性

## 📁 检查的文件列表

1. `..\autoBMAD\epic_automation\__init__.py`
2. `..\autoBMAD\epic_automation\agents\__init__.py`
3. `..\autoBMAD\epic_automation\agents\base_agent.py`
4. `..\autoBMAD\epic_automation\agents\dev_agent.py`
5. `..\autoBMAD\epic_automation\agents\qa_agent.py`
6. `..\autoBMAD\epic_automation\agents\quality_agents.py`
7. `..\autoBMAD\epic_automation\agents\sdk_helper.py`
8. `..\autoBMAD\epic_automation\agents\sm_agent.py`
9. `..\autoBMAD\epic_automation\agents\state_agent.py`
10. `..\autoBMAD\epic_automation\controllers\__init__.py`
11. `..\autoBMAD\epic_automation\controllers\base_controller.py`
12. `..\autoBMAD\epic_automation\controllers\devqa_controller.py`
13. `..\autoBMAD\epic_automation\controllers\quality_controller.py`
14. `..\autoBMAD\epic_automation\controllers\sm_controller.py`
15. `..\autoBMAD\epic_automation\core\__init__.py`
16. `..\autoBMAD\epic_automation\core\cancellation_manager.py`
17. `..\autoBMAD\epic_automation\core\sdk_executor.py`
18. `..\autoBMAD\epic_automation\core\sdk_result.py`
19. `..\autoBMAD\epic_automation\epic_driver.py`
20. `..\autoBMAD\epic_automation\init_db.py`
21. `..\autoBMAD\epic_automation\log_manager.py`
22. `..\autoBMAD\epic_automation\monitoring\__init__.py`
23. `..\autoBMAD\epic_automation\monitoring\resource_monitor.py`
24. `..\autoBMAD\epic_automation\sdk_wrapper.py`
25. `..\autoBMAD\epic_automation\state_manager.py`
26. `..\autoBMAD\epic_automation\tests\test_cancellation_manager.py`
27. `..\autoBMAD\epic_automation\tests\test_sdk_result.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:8:8 - error: "os" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:10:8 - error: "time" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:742:41 - error: "PathlibPath" 导入项未使用 (reportUnusedImport)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1124:58 - error: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
    "None" 与 "bool" 不兼容 (reportReturnType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1175:79 - error: 根据标注的返回类型，该函数必须在所有代码路径上返回 "bool" 类型的值
    "None" 与 "bool" 不兼容 (reportReturnType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:732:62 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:732:64 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:5:8 - error: "anyio" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:6:27 - error: "MagicMock" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:65:24 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:66:24 - error: "_lock" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:73:36 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:74:29 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:87:28 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:88:36 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:89:36 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:90:36 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:99:29 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:108:29 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:117:50 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:125:29 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:134:50 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:142:29 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:151:50 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:176:40 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:185:36 - error: "_active_calls" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:262:26 - error: `None` 没有 "cleanup_completed" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:276:26 - error: `None` 没有 "cleanup_completed" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:288:26 - error: `None` 没有 "cleanup_completed" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:304:26 - error: `None` 没有 "cancel_requested" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:309:26 - error: `None` 没有 "cleanup_completed" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:318:26 - error: `None` 没有 "has_target_result" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:331:27 - error: `None` 没有 "agent_name" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:332:27 - error: `None` 没有 "agent_name" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:333:27 - error: `None` 没有 "agent_name" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:337:27 - error: `None` 没有 "cancel_requested" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:338:27 - error: `None` 没有 "cancel_requested" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:339:27 - error: `None` 没有 "cancel_requested" 属性 (reportOptionalMemberAccess)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\tests\test_cancellation_manager.py:353:28 - error: `None` 没有 "agent_name" 属性 (reportOptionalMemberAccess)
39 errors, 0 warnings, 0 notes
```


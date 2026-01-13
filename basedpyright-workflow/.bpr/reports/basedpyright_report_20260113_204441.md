# BasedPyright 检查报告
**生成时间**: 2026-01-13 20:44:41
**检查时间**: 2026-01-13T20:44:41.569714
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 38 |
| ❌ 错误 (Error) | 11 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.19 秒 |

## 🔴 错误详情

共发现 **11** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py`: 4 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py`: 1 个错误

### 按规则分组

- `reportUnknownArgumentType`: 7 次
- `reportUnusedImport`: 2 次
- `reportOptionalMemberAccess`: 1 次
- `reportPossiblyUnboundVariable`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:19

- **规则**: `reportUnusedImport`
- **位置**: 第 19 行, 第 11 列
- **错误信息**: "anthropic" 导入项未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:161

- **规则**: `reportOptionalMemberAccess`
- **位置**: 第 161 行, 第 24 列
- **错误信息**: `None` 没有 "close" 属性

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:7

- **规则**: `reportUnusedImport`
- **位置**: 第 7 行, 第 7 列
- **错误信息**: "asyncio" 导入项未使用

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:123

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 123 行, 第 63 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:188

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 188 行, 第 28 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:265

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 265 行, 第 15 列
- **错误信息**: "asyncio" 可能未绑定

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:891

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 891 行, 第 58 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "join" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:903

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 903 行, 第 50 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "join" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent.py:290

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 290 行, 第 33 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent.py:295

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 295 行, 第 38 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:982

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 982 行, 第 57 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "len" 函数中的 "obj" 形参
  参数类型为 "list[Unknown]"

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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:19:12 - error: "anthropic" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\base_agent.py:161:25 - error: `None` 没有 "close" 属性 (reportOptionalMemberAccess)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:7:8 - error: "asyncio" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:123:64 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:188:29 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\pytest_batch_executor.py:265:16 - error: "asyncio" 可能未绑定 (reportPossiblyUnboundVariable)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:891:59 - error: 部分参数的类型未知
    实参对应于 "join" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\sm_agent.py:903:51 - error: 部分参数的类型未知
    实参对应于 "join" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent.py:290:34 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\agents\status_update_agent.py:295:39 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:982:58 - error: 部分参数的类型未知
    实参对应于 "len" 函数中的 "obj" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
11 errors, 0 warnings, 0 notes
```


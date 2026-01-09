# BasedPyright 检查报告
**生成时间**: 2026-01-08 20:31:55
**检查时间**: 2026-01-08T20:31:54.801552
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 18 |
| ❌ 错误 (Error) | 19 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.05 秒 |

## 🔴 错误详情

共发现 **19** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py`: 7 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py`: 4 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_status_parser.py`: 3 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 1 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py`: 1 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_simple.py`: 1 个错误

### 按规则分组

- `reportUnusedVariable`: 4 次
- `reportPossiblyUnboundVariable`: 4 次
- `reportUnknownParameterType`: 3 次
- `reportMissingParameterType`: 3 次
- `reportUnusedImport`: 2 次
- `reportUnknownArgumentType`: 2 次
- `reportPrivateUsage`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1077

- **规则**: `reportUnusedVariable`
- **位置**: 第 1077 行, 第 16 列
- **错误信息**: 变量 "i" 未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:189

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 189 行, 第 12 列
- **错误信息**: "process" 可能未绑定

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:237

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 237 行, 第 12 列
- **错误信息**: "process" 可能未绑定

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:452

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 452 行, 第 12 列
- **错误信息**: "process" 可能未绑定

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:500

- **规则**: `reportPossiblyUnboundVariable`
- **位置**: 第 500 行, 第 12 列
- **错误信息**: "process" 可能未绑定

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:103

- **规则**: `reportUnusedVariable`
- **位置**: 第 103 行, 第 29 列
- **错误信息**: 变量 "process" 未使用

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:696

- **规则**: `reportUnusedVariable`
- **位置**: 第 696 行, 第 12 列
- **错误信息**: 变量 "pattern_found" 未使用

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:710

- **规则**: `reportUnusedVariable`
- **位置**: 第 710 行, 第 24 列
- **错误信息**: 变量 "pattern_found" 未使用

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:10

- **规则**: `reportUnusedImport`
- **位置**: 第 10 行, 第 19 列
- **错误信息**: "Optional" 导入项未使用

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:18

- **规则**: `reportUnknownParameterType`
- **位置**: 第 18 行, 第 23 列
- **错误信息**: "sdk_wrapper" 参数的类型部分未知
  参数为 "Unknown | None" 类型

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:18

- **规则**: `reportMissingParameterType`
- **位置**: 第 18 行, 第 23 列
- **错误信息**: "sdk_wrapper" 参数缺少类型注解

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:243

- **规则**: `reportUnknownParameterType`
- **位置**: 第 243 行, 第 25 列
- **错误信息**: "sdk_wrapper" 参数的类型部分未知
  参数为 "Unknown | None" 类型

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:243

- **规则**: `reportMissingParameterType`
- **位置**: 第 243 行, 第 25 列
- **错误信息**: "sdk_wrapper" 参数缺少类型注解

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:257

- **规则**: `reportUnknownParameterType`
- **位置**: 第 257 行, 第 37 列
- **错误信息**: "sdk_wrapper" 参数的类型部分未知
  参数为 "Unknown | None" 类型

#### 15. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:257

- **规则**: `reportMissingParameterType`
- **位置**: 第 257 行, 第 37 列
- **错误信息**: "sdk_wrapper" 参数缺少类型注解

#### 16. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_simple.py:106

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 106 行, 第 11 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "all" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

#### 17. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_status_parser.py:8

- **规则**: `reportUnusedImport`
- **位置**: 第 8 行, 第 7 列
- **错误信息**: "os" 导入项未使用

#### 18. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_status_parser.py:173

- **规则**: `reportPrivateUsage`
- **位置**: 第 173 行, 第 24 列
- **错误信息**: "_normalize_status" 在声明它受到保护的类之外被使用

#### 19. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_status_parser.py:201

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 201 行, 第 11 列
- **错误信息**: 部分参数的类型未知
  实参对应于 "all" 函数中的 "iterable" 形参
  参数类型为 "list[Unknown]"

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
14. `..\autoBMAD\epic_automation\status_parser.py`
15. `..\autoBMAD\epic_automation\test_automation_agent.py`
16. `..\autoBMAD\epic_automation\test_logging.py`
17. `..\autoBMAD\epic_automation\test_simple.py`
18. `..\autoBMAD\epic_automation\test_status_parser.py`

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:1077:17 - error: 变量 "i" 未使用 (reportUnusedVariable)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:189:13 - error: "process" 可能未绑定 (reportPossiblyUnboundVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:237:13 - error: "process" 可能未绑定 (reportPossiblyUnboundVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:452:13 - error: "process" 可能未绑定 (reportPossiblyUnboundVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_tools_integration.py:500:13 - error: "process" 可能未绑定 (reportPossiblyUnboundVariable)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:103:30 - error: 变量 "process" 未使用 (reportUnusedVariable)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:696:13 - error: 变量 "pattern_found" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\state_manager.py:710:25 - error: 变量 "pattern_found" 未使用 (reportUnusedVariable)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:10:20 - error: "Optional" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:18:24 - error: "sdk_wrapper" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:18:24 - error: "sdk_wrapper" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:243:26 - error: "sdk_wrapper" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:243:26 - error: "sdk_wrapper" 参数缺少类型注解 (reportMissingParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:257:38 - error: "sdk_wrapper" 参数的类型部分未知
    参数为 "Unknown | None" 类型 (reportUnknownParameterType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:257:38 - error: "sdk_wrapper" 参数缺少类型注解 (reportMissingParameterType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_simple.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_simple.py:106:12 - error: 部分参数的类型未知
    实参对应于 "all" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_status_parser.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_status_parser.py:8:8 - error: "os" 导入项未使用 (reportUnusedImport)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_status_parser.py:173:25 - error: "_normalize_status" 在声明它受到保护的类之外被使用 (reportPrivateUsage)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\test_status_parser.py:201:12 - error: 部分参数的类型未知
    实参对应于 "all" 函数中的 "iterable" 形参
    参数类型为 "list[Unknown]" (reportUnknownArgumentType)
19 errors, 0 warnings, 0 notes
```


# BasedPyright 检查报告
**生成时间**: 2026-01-09 00:46:00
**检查时间**: 2026-01-09T00:46:00.176439
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 14 |
| ❌ 错误 (Error) | 6 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.08 秒 |

## 🔴 错误详情

共发现 **6** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py`: 1 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 1 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py`: 1 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py`: 1 个错误

### 按规则分组

- `reportArgumentType`: 4 次
- `reportUnnecessaryIsInstance`: 1 次
- `reportUnusedVariable`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:75

- **规则**: `reportArgumentType`
- **位置**: 第 75 行, 第 58 列
- **错误信息**: "type[SafeClaudeSDK] | None" 类型的实参无法赋值给函数 "__init__" 中 "SafeClaudeSDK | None" 类型的形参 "sdk_wrapper"
  "type[SafeClaudeSDK] | None" 类型与 "SafeClaudeSDK | None" 类型不兼容
    "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK | None" 类型不兼容
      "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK" 类型不兼容
      类型与 `None` 不匹配

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:587

- **规则**: `reportArgumentType`
- **位置**: 第 587 行, 第 62 列
- **错误信息**: "type[SafeClaudeSDK]" 类型的实参无法赋值给函数 "__init__" 中 "SafeClaudeSDK | None" 类型的形参 "sdk_wrapper"
  "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK | None" 类型不兼容
    "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK" 类型不兼容
    类型与 `None` 不匹配

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:139

- **规则**: `reportArgumentType`
- **位置**: 第 139 行, 第 58 列
- **错误信息**: "type[SafeClaudeSDK]" 类型的实参无法赋值给函数 "__init__" 中 "SafeClaudeSDK | None" 类型的形参 "sdk_wrapper"
  "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK | None" 类型不兼容
    "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK" 类型不兼容
    类型与 `None` 不匹配

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:55

- **规则**: `reportArgumentType`
- **位置**: 第 55 行, 第 58 列
- **错误信息**: "type[SafeClaudeSDK]" 类型的实参无法赋值给函数 "__init__" 中 "SafeClaudeSDK | None" 类型的形参 "sdk_wrapper"
  "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK | None" 类型不兼容
    "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK" 类型不兼容
    类型与 `None` 不匹配

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:208

- **规则**: `reportUnnecessaryIsInstance`
- **位置**: 第 208 行, 第 15 列
- **错误信息**: "SafeClaudeSDK" 一定是 "SafeClaudeSDK" 的实例，无需再调用 `isinstance`

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:318

- **规则**: `reportUnusedVariable`
- **位置**: 第 318 行, 第 8 列
- **错误信息**: 变量 "loop" 未使用

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

## 📄 原始检查输出

```
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:75:59 - error: "type[SafeClaudeSDK] | None" 类型的实参无法赋值给函数 "__init__" 中 "SafeClaudeSDK | None" 类型的形参 "sdk_wrapper"
    "type[SafeClaudeSDK] | None" 类型与 "SafeClaudeSDK | None" 类型不兼容
      "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK | None" 类型不兼容
        "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK" 类型不兼容
        类型与 `None` 不匹配 (reportArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:587:63 - error: "type[SafeClaudeSDK]" 类型的实参无法赋值给函数 "__init__" 中 "SafeClaudeSDK | None" 类型的形参 "sdk_wrapper"
    "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK | None" 类型不兼容
      "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK" 类型不兼容
      类型与 `None` 不匹配 (reportArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\qa_agent.py:139:59 - error: "type[SafeClaudeSDK]" 类型的实参无法赋值给函数 "__init__" 中 "SafeClaudeSDK | None" 类型的形参 "sdk_wrapper"
    "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK | None" 类型不兼容
      "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK" 类型不兼容
      类型与 `None` 不匹配 (reportArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\sm_agent.py:55:59 - error: "type[SafeClaudeSDK]" 类型的实参无法赋值给函数 "__init__" 中 "SafeClaudeSDK | None" 类型的形参 "sdk_wrapper"
    "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK | None" 类型不兼容
      "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK" 类型不兼容
      类型与 `None` 不匹配 (reportArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:208:16 - error: "SafeClaudeSDK" 一定是 "SafeClaudeSDK" 的实例，无需再调用 `isinstance` (reportUnnecessaryIsInstance)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:318:9 - error: 变量 "loop" 未使用 (reportUnusedVariable)
6 errors, 0 warnings, 0 notes
```


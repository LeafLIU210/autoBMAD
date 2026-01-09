# BasedPyright 检查报告
**生成时间**: 2026-01-09 00:29:27
**检查时间**: 2026-01-09T00:29:27.472450
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 14 |
| ❌ 错误 (Error) | 14 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.01 秒 |

## 🔴 错误详情

共发现 **14** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 9 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py`: 4 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py`: 1 个错误

### 按规则分组

- `reportUnusedVariable`: 6 次
- `reportInvalidStringEscapeSequence`: 5 次
- `reportUnusedFunction`: 1 次
- `reportUndefinedVariable`: 1 次
- `reportUnknownArgumentType`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:104

- **规则**: `reportUnusedFunction`
- **位置**: 第 104 行, 第 4 列
- **错误信息**: "_convert_core_to_processing_status" 函数未使用

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:344

- **规则**: `reportUnusedVariable`
- **位置**: 第 344 行, 第 12 列
- **错误信息**: 变量 "state_manager" 未使用

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:580

- **规则**: `reportUndefinedVariable`
- **位置**: 第 580 行, 第 62 列
- **错误信息**: "SafeClaudeSDK" 未定义

#### 4. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:580

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 580 行, 第 62 列
- **错误信息**: 参数类型未知
  实参对应于 "__init__" 函数中的 "sdk_wrapper" 形参

#### 5. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:853

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 853 行, 第 10 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 6. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:853

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 853 行, 第 17 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 7. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:853

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 853 行, 第 32 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 8. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:853

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 853 行, 第 37 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 9. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:868

- **规则**: `reportInvalidStringEscapeSequence`
- **位置**: 第 868 行, 第 36 列
- **错误信息**: 字符串字面量中有不受支持的转义序列

#### 10. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:112

- **规则**: `reportUnusedVariable`
- **位置**: 第 112 行, 第 28 列
- **错误信息**: 变量 "stderr" 未使用

#### 11. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:112

- **规则**: `reportUnusedVariable`
- **位置**: 第 112 行, 第 36 列
- **错误信息**: 变量 "returncode" 未使用

#### 12. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:120

- **规则**: `reportUnusedVariable`
- **位置**: 第 120 行, 第 36 列
- **错误信息**: 变量 "stderr" 未使用

#### 13. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:120

- **规则**: `reportUnusedVariable`
- **位置**: 第 120 行, 第 44 列
- **错误信息**: 变量 "returncode" 未使用

#### 14. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:302

- **规则**: `reportUnusedVariable`
- **位置**: 第 302 行, 第 8 列
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
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:104:5 - error: "_convert_core_to_processing_status" 函数未使用 (reportUnusedFunction)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:344:13 - error: 变量 "state_manager" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:580:63 - error: "SafeClaudeSDK" 未定义 (reportUndefinedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:580:63 - error: 参数类型未知
    实参对应于 "__init__" 函数中的 "sdk_wrapper" 形参 (reportUnknownArgumentType)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:853:11 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:853:18 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:853:33 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:853:38 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:868:37 - error: 字符串字面量中有不受支持的转义序列 (reportInvalidStringEscapeSequence)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:112:29 - error: 变量 "stderr" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:112:37 - error: 变量 "returncode" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:120:37 - error: 变量 "stderr" 未使用 (reportUnusedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\quality_agents.py:120:45 - error: 变量 "returncode" 未使用 (reportUnusedVariable)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:302:9 - error: 变量 "loop" 未使用 (reportUnusedVariable)
14 errors, 0 warnings, 0 notes
```


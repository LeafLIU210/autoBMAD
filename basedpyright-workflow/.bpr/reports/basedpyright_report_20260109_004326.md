# BasedPyright 检查报告
**生成时间**: 2026-01-09 00:43:26
**检查时间**: 2026-01-09T00:43:25.850384
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 14 |
| ❌ 错误 (Error) | 3 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.04 秒 |

## 🔴 错误详情

共发现 **3** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py`: 1 个错误

### 按规则分组

- `reportUndefinedVariable`: 1 次
- `reportUnknownArgumentType`: 1 次
- `reportUnusedVariable`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:584

- **规则**: `reportUndefinedVariable`
- **位置**: 第 584 行, 第 62 列
- **错误信息**: "SafeClaudeSDK" 未定义

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:584

- **规则**: `reportUnknownArgumentType`
- **位置**: 第 584 行, 第 62 列
- **错误信息**: 参数类型未知
  实参对应于 "__init__" 函数中的 "sdk_wrapper" 形参

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:302

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
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:584:63 - error: "SafeClaudeSDK" 未定义 (reportUndefinedVariable)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:584:63 - error: 参数类型未知
    实参对应于 "__init__" 函数中的 "sdk_wrapper" 形参 (reportUnknownArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\status_parser.py:302:9 - error: 变量 "loop" 未使用 (reportUnusedVariable)
3 errors, 0 warnings, 0 notes
```


# BasedPyright 检查报告
**生成时间**: 2026-01-09 00:59:17
**检查时间**: 2026-01-09T00:59:17.328731
**检查目录**: `..\autoBMAD\epic_automation`

## 📊 执行摘要

| 项目 | 数量 |
|------|------|
| 检查文件数 | 14 |
| ❌ 错误 (Error) | 3 |
| ⚠️ 警告 (Warning) | 0 |
| ℹ️ 信息 (Information) | 0 |
| ⏱️ 检查耗时 | 1.05 秒 |

## 🔴 错误详情

共发现 **3** 个错误

### 按文件分组

- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py`: 2 个错误
- `d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py`: 1 个错误

### 按规则分组

- `reportArgumentType`: 1 次
- `reportRedeclaration`: 1 次
- `reportCallIssue`: 1 次

### 详细错误列表

#### 1. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:69

- **规则**: `reportArgumentType`
- **位置**: 第 69 行, 第 58 列
- **错误信息**: "type[SafeClaudeSDK] | None" 类型的实参无法赋值给函数 "__init__" 中 "SafeClaudeSDK | None" 类型的形参 "sdk_wrapper"
  "type[SafeClaudeSDK] | None" 类型与 "SafeClaudeSDK | None" 类型不兼容
    "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK | None" 类型不兼容
      "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK" 类型不兼容
      类型与 `None` 不匹配

#### 2. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:151

- **规则**: `reportRedeclaration`
- **位置**: 第 151 行, 第 4 列
- **错误信息**: "results" 变量声明被同名声明遮蔽

#### 3. d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:598

- **规则**: `reportCallIssue`
- **位置**: 第 598 行, 第 62 列
- **错误信息**: 参数 "prompt", "options" 缺少传入值

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
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\dev_agent.py:69:59 - error: "type[SafeClaudeSDK] | None" 类型的实参无法赋值给函数 "__init__" 中 "SafeClaudeSDK | None" 类型的形参 "sdk_wrapper"
    "type[SafeClaudeSDK] | None" 类型与 "SafeClaudeSDK | None" 类型不兼容
      "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK | None" 类型不兼容
        "type[SafeClaudeSDK]" 类型与 "SafeClaudeSDK" 类型不兼容
        类型与 `None` 不匹配 (reportArgumentType)
d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:151:5 - error: "results" 变量声明被同名声明遮蔽 (reportRedeclaration)
  d:\GITHUB\pytQt_template\autoBMAD\epic_automation\epic_driver.py:598:63 - error: 参数 "prompt", "options" 缺少传入值 (reportCallIssue)
3 errors, 0 warnings, 0 notes
```

